from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from apps.core.viewsets import TenantModelViewSet
from apps.core.permissions import IsVerifiedTeacher, IsTeacherOwnerOrReadOnly
from apps.core.utils import log_activity
from .models import Course, Unit, ActivationCode
from .serializers import (
    CourseSerializer, UnitSerializer,
    ActivationCodeSerializer, CourseDetailSerializer,
)
from django.conf import settings
from datetime import timedelta


# ────────────────────────────────────────────────────────────────────
# Standard ViewSets
# ────────────────────────────────────────────────────────────────────

class CourseViewSet(TenantModelViewSet):

    queryset = Course.objects.select_related('teacher').annotate(
        units_count=Count('units', distinct=True)
    )
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['teacher']
    search_fields = ['title']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [
                IsAuthenticated(),
                IsTeacherOwnerOrReadOnly(),
                IsVerifiedTeacher(),
            ]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        course = serializer.save(teacher=self.request.user.teacher_profile)
        log_activity(
            user=self.request.user,
            action="أنشأ كورس",
            description=f"أنشأ كورس جديد: {course.title}"
        )


class UnitViewSet(TenantModelViewSet):
    """
    وحدات الكورس: Course → Unit → Lesson
    """
    queryset = Unit.objects.select_related('course', 'teacher')
    serializer_class = UnitSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [
                IsAuthenticated(),
                IsTeacherOwnerOrReadOnly(),
                IsVerifiedTeacher(),
            ]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        unit = serializer.save(teacher=self.request.user.teacher_profile)
        log_activity(
            user=self.request.user,
            action="أنشأ وحدة",
            description=f"أنشأ وحدة: {unit.title} في كورس: {unit.course.title}"
        )


# ────────────────────────────────────────────────────────────────────
# Course Detail Public Page
# ────────────────────────────────────────────────────────────────────

class CourseDetailPublicView(APIView):
    """
    GET /api/courses/{course_id}/detail/
    صفحة تفاصيل الكورس للطالب:
    - بيانات الكورس الكاملة
    - اسم المدرس + صورته + أرقام التواصل معه للدفع
    - قائمة الوحدات والدروس المنشورة
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(
            Course.objects.select_related('teacher__user').prefetch_related(
                'units__lessons'
            ),
            pk=course_id,
            is_published=True,
        )
        serializer = CourseDetailSerializer(course, context={'request': request})
        return Response(serializer.data)


# ────────────────────────────────────────────────────────────────────
# Activation Code — Teacher Dashboard
# ────────────────────────────────────────────────────────────────────

class GenerateCodesView(APIView):
    """
    POST /api/courses/{course_id}/generate-codes/
    المدرس يطلب توليد أكواد جديدة للكورس (max 25 في المرة الواحدة).
    Body: { "count": 1-25 }
    """
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def post(self, request, course_id):
        teacher = request.user.teacher_profile
        course = get_object_or_404(Course, pk=course_id, teacher=teacher)

        count = request.data.get('count', 1)
        try:
            count = int(count)
        except (TypeError, ValueError):
            return Response({'detail': 'العدد يجب أن يكون رقماً.'}, status=status.HTTP_400_BAD_REQUEST)

        if count < 1 or count > 25:
            return Response(
                {'detail': 'الحد الأقصى لتوليد الأكواد هو 25 في المرة الواحدة، والحد الأدنى 1.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # نُولّد الأكواد في عملية واحدة مضمونة
        codes = []
        with transaction.atomic():
            for _ in range(count):
                code_obj = ActivationCode(course=course, created_by=teacher)
                code_obj.save()  # auto-generates unique code in model.save()
                codes.append(code_obj)

        serializer = ActivationCodeSerializer(codes, many=True)
        return Response({
            'generated': count,
            'codes': serializer.data,
        }, status=status.HTTP_201_CREATED)


class ListCodesView(APIView):
    """
    GET /api/courses/{course_id}/codes/?status=used|unused
    المدرس يرى كل أكواد الكورس مع حالة كل كود.
    مدمج معها Pagination لتجنب تحميل آلاف الأكواد دفعة واحدة.
    """
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def get(self, request, course_id):
        from rest_framework.pagination import PageNumberPagination
        teacher = request.user.teacher_profile
        course = get_object_or_404(Course, pk=course_id, teacher=teacher)

        qs = ActivationCode.objects.filter(
            course=course, created_by=teacher
        ).select_related('used_by__user').order_by('-created_at')

        # Optional filter
        filter_status = request.query_params.get('status')
        if filter_status == 'used':
            qs = qs.filter(is_used=True)
        elif filter_status == 'unused':
            qs = qs.filter(is_used=False)

        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(qs, request)
        
        if page is not None:
            serializer = ActivationCodeSerializer(page, many=True)
            return paginator.get_paginated_response({
                'course': course.title,
                'codes': serializer.data
            })

        serializer = ActivationCodeSerializer(qs, many=True)
        return Response({
            'course': course.title,
            'total': qs.count(),
            'codes': serializer.data,
        })


# ────────────────────────────────────────────────────────────────────
# Redeem Code — Student
# ────────────────────────────────────────────────────────────────────

class RedeemCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'detail': 'فقط الطلاب يمكنهم استخدام أكواد التفعيل.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        code_value = request.data.get('code', '').strip()
        if not code_value:
            return Response(
                {'detail': 'كود التفعيل مطلوب.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        student = request.user.student_profile

        from apps.students.models import Enrollment

        try:
            with transaction.atomic():

                code_obj = (
                    ActivationCode.objects
                    .select_for_update()
                    .select_related('course')
                    .get(code=code_value)
                )

                if code_obj.is_used:
                    return Response(
                        {'detail': 'هذا الكود مستخدم بالفعل وانتهت صلاحيته.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                course = code_obj.course

                enrollment_qs = Enrollment.objects.select_for_update().filter(
                    student=student,
                    course=course
                )

                today = timezone.now().date()
                expiry = today + timedelta(days=settings.COURSE_SUBSCRIPTION_DAYS)

                if enrollment_qs.exists():
                    enrollment = enrollment_qs.first()

                    if enrollment.is_active:
                        return Response(
                            {'detail': 'أنت مشترك في هذا الكورس بالفعل.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    enrollment.start_date = today
                    enrollment.expiry_date = expiry
                    enrollment.is_active = True
                    enrollment.is_pending = False
                    enrollment.save(update_fields=[
                        'start_date',
                        'expiry_date',
                        'is_active',
                        'is_pending',
                    ])
                else:
                    enrollment = Enrollment.objects.create(
                        student=student,
                        course=course,
                        phone_number=student.phone_number,
                        parent_phone=student.parent_phone,
                        start_date=today,
                        expiry_date=expiry,
                        is_active=True,
                        is_pending=False,
                    )

                code_obj.is_used = True
                code_obj.used_by = student
                code_obj.used_at = timezone.now()
                code_obj.save(update_fields=['is_used', 'used_by', 'used_at'])

        except ActivationCode.DoesNotExist:
            return Response(
                {'detail': 'الكود غير صحيح.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'detail': 'تم تفعيل اشتراكك بنجاح!',
            'course': course.title,
            'expiry_date': expiry.isoformat(),
        }, status=status.HTTP_200_OK)


# ────────────────────────────────────────────────────────────────────
# Student Progress Tab — Teacher Dashboard
# ────────────────────────────────────────────────────────────────────

class CourseStudentProgressView(APIView):
    """
    GET /api/courses/{course_id}/student-progress/
    المدرس يرى جدول تقدم الطلاب المشتركين في الكورس.
    """
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def get(self, request, course_id):
        teacher = request.user.teacher_profile
        course = get_object_or_404(Course, pk=course_id, teacher=teacher)

        from apps.students.models import Enrollment
        from apps.progress.models import LessonProgress
        from apps.lessons.models import Lesson

        enrollments = (
            Enrollment.objects
            .filter(course=course, is_active=True)
            .select_related('student__user')
            .order_by('student__user__first_name')
        )

        lessons = list(
            Lesson.objects.filter(course=course, is_published=True).order_by('order')
        )
        lesson_ids = [l.id for l in lessons]

        # جلب كل تقدم دفعة واحدة
        progress_records = LessonProgress.objects.filter(
            lesson_id__in=lesson_ids,
        ).values('student_id', 'lesson_id', 'lesson_completed', 'watched_percentage')

        # فهرسة التقدم: { student_id: { lesson_id: {...} } }
        progress_map = {}
        for pr in progress_records:
            sid = pr['student_id']
            lid = pr['lesson_id']
            if sid not in progress_map:
                progress_map[sid] = {}
            progress_map[sid][lid] = pr

        result = []
        for enrollment in enrollments:
            student = enrollment.student
            student_progress = progress_map.get(student.id, {})

            lessons_status = []
            completed_count = 0
            for lesson in lessons:
                pr = student_progress.get(lesson.id)
                completed = pr['lesson_completed'] if pr else False
                if completed:
                    completed_count += 1
                lessons_status.append({
                    'lesson_id': lesson.id,
                    'lesson_title': lesson.title,
                    'lesson_order': lesson.order,
                    'completed': completed,
                    'watched_percentage': pr['watched_percentage'] if pr else 0,
                })

            total = len(lessons)
            result.append({
                'student_id': student.id,
                'student_name': student.user.get_full_name(),
                'student_phone': student.user.phone,
                'parent_phone': student.parent_phone,
                'enrollment_expiry': enrollment.expiry_date,
                'completed_lessons': completed_count,
                'total_lessons': total,
                'completion_rate': round((completed_count / total * 100) if total else 0, 1),
                'lessons_progress': lessons_status,
            })

        return Response({
            'course': course.title,
            'total_students': len(result),
            'students': result,
        })


