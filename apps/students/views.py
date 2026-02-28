from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from django.conf import settings

from .models import Enrollment, Student
from .serializers import EnrollmentSerializer
from apps.core.permissions import IsVerifiedTeacher
from apps.social.models import Post, PostLike
from apps.teachers.models import Follow


class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, "student_profile"):
            return Response(
                {"detail": "هذا المستخدم لا يملك ملف طالب."},
                status=400
            )

        student = request.user.student_profile

        following_count = Follow.objects.filter(user=request.user).count()
        posts_count = Post.objects.filter(author_student=student).count()
        likes_count = PostLike.objects.filter(
            post__author_student=student
        ).count()

        return Response({
            "id": student.id,
            "name": request.user.get_full_name(),
            "email": request.user.email,
            "serial_number": request.user.serial_number,
            "phone": request.user.phone,
            "parent_phone": student.parent_phone,
            "image": request.user.image.url if request.user.image else None,
            "stats": {
                "following": following_count,
                "posts": posts_count,
                "likes": likes_count
            }
        })


class StudentPublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, student_id):
        student = get_object_or_404(
            Student.objects.select_related('user'),
            id=student_id
        )

        user = student.user

        following_count = Follow.objects.filter(user=user).count()
        posts_count = Post.objects.filter(
            author_student=student
        ).count()
        likes_count = PostLike.objects.filter(
            post__author_student=student
        ).count()

        return Response({
            "id": student.id,
            "name": user.get_full_name(),
            "image": user.image.url if user.image else None,
            "stats": {
                "following": following_count,
                "posts": posts_count,
                "likes": likes_count
            }
        })


# ✅ BUG-10 FIX (Optimized & Safe)
class StudentLookupView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def post(self, request):
        serials = request.data.get('serials', [])

        if not isinstance(serials, list) or not serials:
            return Response(
                {"detail": "قائمة الأرقام التسلسلية مطلوبة."},
                status=400
            )

        # إزالة التكرار
        serials = list(set(serials))

        # Query واحدة فقط
        students_qs = Student.objects.filter(
            user__serial_number__in=serials
        ).select_related('user')

        students_map = {
            s.user.serial_number: s
            for s in students_qs
        }

        results = []

        for sn in serials:
            student = students_map.get(sn)

            if not student:
                results.append({
                    "serial_number": sn,
                    "status": "not_found"
                })
                continue

            results.append({
                "serial_number": student.user.serial_number,
                "name": student.user.get_full_name(),
                "phone": student.user.phone,
                "email": student.user.email,
                "parent_phone": student.parent_phone,
                "status": "found"
            })

        return Response({
            "processed": len(serials),
            "results": results
        })


class BulkActivateRenewView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def post(self, request, *args, **kwargs):
        serials = request.data.get('serials', [])

        if not isinstance(serials, list) or not serials:
            return Response(
                {"detail": "قائمة الأرقام التسلسلية مطلوبة."},
                status=400
            )

        serials = list(set(serials))

        teacher = request.user.teacher_profile
        today = timezone.now().date()
        expiry = today + timedelta(
            days=settings.COURSE_SUBSCRIPTION_DAYS
        )

        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {"detail": "course_id مطلوب."},
                status=400
            )

        from apps.courses.models import Course
        course = get_object_or_404(
            Course,
            id=course_id,
            teacher=teacher
        )

        students_map = {
            s.user.serial_number: s
            for s in Student.objects.filter(
                user__serial_number__in=serials
            ).select_related("user")
        }

        results = []

        for sn in serials:
            student = students_map.get(sn)

            if not student:
                results.append({
                    "serial": sn,
                    "status": "not_found"
                })
                continue

            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    'phone_number': student.phone_number or student.user.phone,
                    'parent_phone': student.parent_phone,
                    'start_date': today,
                    'expiry_date': expiry,
                    'is_active': True,
                    'is_pending': False,
                }
            )

            if not created:
                enrollment.phone_number = student.phone_number or student.user.phone
                enrollment.parent_phone = student.parent_phone
                enrollment.start_date = today
                enrollment.expiry_date = expiry
                enrollment.is_active = True
                enrollment.is_pending = False
                enrollment.save(update_fields=[
                    'phone_number',
                    'parent_phone',
                    'start_date',
                    'expiry_date',
                    'is_active',
                    'is_pending'
                ])

            results.append({
                "serial": sn,
                "status": "activated",
                "expiry": expiry
            })

        return Response({
            "processed": len(serials),
            "results": results
        })


class StudentMonitoringView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def get(self, request):
        lesson_id = request.query_params.get('lesson_id')
        filter_type = request.query_params.get('filter')

        teacher = request.user.teacher_profile

        enrollments = Enrollment.objects.filter(
            course__teacher=teacher,
            is_active=True,
            expiry_date__gte=timezone.now().date()
        ).select_related('student__user')

        data = []

        if filter_type == 'not_watched' and lesson_id:
            from apps.progress.models import LessonProgress

            watched_ids = LessonProgress.objects.filter(
                lesson_id=lesson_id,
                video_completed=True
            ).values_list('student_id', flat=True)

            students = enrollments.exclude(
                student_id__in=watched_ids
            )

        elif filter_type == 'inactive_72h':
            time_threshold = timezone.now() - timedelta(hours=72)
            students = enrollments.filter(
                student__user__last_login__lt=time_threshold
            )
        else:
            students = []

        for en in students:
            data.append({
                "name": en.student.user.get_full_name(),
                "phone": en.student.user.phone,
                "parent_phone": en.student.parent_phone,
                "last_login": en.student.user.last_login
            })

        return Response(data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    queryset = Enrollment.objects.select_related(
        'student__user',
        'course'
    )
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'teacher_profile'):
            return self.queryset.filter(
                course__teacher=user.teacher_profile
            )

        if hasattr(user, 'student_profile'):
            return self.queryset.filter(
                student=user.student_profile
            )

        return self.queryset.none()