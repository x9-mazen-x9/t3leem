from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Q

from apps.students.serializers import StudentProfileSerializer
from rest_framework import viewsets
from .models import Enrollment, Student
from .serializers import EnrollmentSerializer
from apps.core.permissions import IsVerifiedTeacher
from django.conf import settings
from apps.students.models import Student
from apps.social.models import Post, PostLike
from apps.teachers.models import Follow

class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # لو المستخدم الحالي مش طالب
        if not hasattr(request.user, "student_profile"):
            return Response({"detail": "هذا المستخدم لا يملك ملف طالب."}, status=400)

        student = request.user.student_profile
        
        # 1. حساب الإحصائيات
        following_count = Follow.objects.filter(user=request.user).count()
        posts_count = Post.objects.filter(author_student=student).count()
        likes_count = PostLike.objects.filter(post__author_student=student).count()

        data = {
            # بيانات أساسية (آمنة)
            "id": student.id,
            "name": request.user.get_full_name(),
            "email": request.user.email,
            "serial_number": student.serial_number, # صاحب الحساب فقط يراه
            "phone": request.user.phone,
            "parent_phone": student.parent_phone,
            
            # صورة البروفايل (لو موجودة)
            "image": request.user.image.url if hasattr(request.user, 'image') and request.user.image else None,

            # إحصائيات
            "stats": {
                "following": following_count,
                "posts": posts_count,
                "likes": likes_count
            }
        }
        return Response(data)

# --- نقطة 7 و 20 و 21: البحث عن طلاب بالكود والتفعيل ---

class StudentLookupView(APIView):
    """
    نقطة 21: المدرس يدخل السيريال نمبر فيظهر له بيانات الطالب
    (الاسم - رقم الهاتف - البريد - رقم ولي الأمر)
    """
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def post(self, request):
        serials = request.data.get('serials', [])
        if not isinstance(serials, list) or not serials:
            return Response({"detail": "قائمة الأرقام التسلسلية مطلوبة."}, status=400)

        students = Student.objects.filter(serial_number__in=serials).select_related('user')
        results = []
        for s in students:
            results.append({
                "serial_number": s.serial_number,
                "name": s.user.get_full_name(),
                "phone": s.user.phone,
                "email": s.user.email,
                "parent_phone": s.parent_phone
            })
        return Response(results)

class BulkActivateRenewView(APIView):
    """
    نقطة 7 و 20: تفعيل اشتراك الطلاب (35 يوم)
    """
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def post(self, request, *args, **kwargs):
        serials = request.data.get('serials', [])
        if not isinstance(serials, list) or not serials:
            return Response({"detail": "قائمة الأرقام التسلسلية مطلوبة."}, status=400)

        teacher = request.user.teacher_profile
        today = timezone.now().date()
        # نقطة 20: مدة الاشتراك 35 يوم
        expiry = today + timedelta(days=settings.COURSE_SUBSCRIPTION_DAYS)
        
        results = []
        for sn in serials:
            try:
                student = Student.objects.get(serial_number=sn)
                # التفعيل
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student, 
                    teacher=teacher,
                    defaults={'course_id': request.data.get('course_id')} # يجب إرسال course_id من الفرونت
                )
                
                # لو الـ enrollment موجود مسبقاً (تجديد)
                if not created:
                    enrollment.expiry_date = expiry
                    enrollment.is_active = True
                    enrollment.is_pending = False
                    enrollment.save()
                else:
                    # لو جديد
                    enrollment.expiry_date = expiry
                    enrollment.is_active = True
                    enrollment.is_pending = False
                    enrollment.save()

                results.append({"serial": sn, "status": "activated", "expiry": expiry})
            except Student.DoesNotExist:
                results.append({"serial": sn, "status": "not_found"})

        return Response({"processed": len(results), "results": results})

# --- نقطة 22: متابعة الطلاب (من لم يشاهد الفيديو) ---

class StudentMonitoringView(APIView):
    """
    نقطة 22: فلترة الطلاب (مشاهد / لم يشاهد) والتحقق من آخر ظهور
    """
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def get(self, request):
        lesson_id = request.query_params.get('lesson_id')
        filter_type = request.query_params.get('filter') # 'not_watched' or 'inactive_72h'
        
        teacher = request.user.teacher_profile
        # جلب طلاب المدرس الفعالين
        enrollments = Enrollment.objects.filter(
            teacher=teacher, 
            is_active=True, 
            expiry_date__gte=timezone.now().date()
        ).select_related('student__user')

        data = []
        
        if filter_type == 'not_watched' and lesson_id:
            # جلب الطلاب اللي شافوا الدرس
            from apps.progress.models import LessonProgress
            watched_ids = LessonProgress.objects.filter(
                lesson_id=lesson_id, 
                video_completed=True
            ).values_list('student_id', flat=True)
            
            # فلترة اللي ماشافوش
            students = enrollments.exclude(student_id__in=watched_ids)
            
            for en in students:
                data.append({
                    "name": en.student.user.get_full_name(),
                    "phone": en.student.user.phone,
                    "parent_phone": en.student.parent_phone,
                    "last_login": en.student.user.last_login
                })

        elif filter_type == 'inactive_72h':
            # طلاب غياب 72 ساعة
            time_threshold = timezone.now() - timedelta(hours=72)
            students = enrollments.filter(student__user__last_login__lt=time_threshold)
            
            for en in students:
                data.append({
                    "name": en.student.user.get_full_name(),
                    "phone": en.student.user.phone,
                    "parent_phone": en.student.parent_phone,
                    "last_login": en.student.user.last_login
                })
            
        return Response(data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]