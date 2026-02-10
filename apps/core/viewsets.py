# apps/core/viewsets.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsTeacherOwnerOrReadOnly, IsStudentOwnerOrReadOnly

class TenantModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet يطبق عزل البيانات بناءً على الاشتراكات (Enrollments).
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # 1. إذا كان المستخدم مدرساً: يرى كل محتواه (الدروس، الطلاب المشتركين معه.. إلخ)
        if hasattr(user, 'teacher_profile'):
            return queryset.filter(teacher=user.teacher_profile)
        
        # 2. إذا كان المستخدم طالباً: يرى محتوى المدرسين الذين اشترك معهم وفعلوا حسابه فقط
        elif hasattr(user, 'student_profile'):
            # جلب قائمة الـ IDs للمدرسين الذين لديهم اشتراكات نشطة مع هذا الطالب
            active_teachers_ids = user.student_profile.enrollments.filter(
                is_active=True  # شرط مهم: فقط المشتركين المفعلين
            ).values_list('teacher_id', flat=True)
            
            # فلترة الدروس/البوستات لتلك المدرسين فقط
            return queryset.filter(teacher_id__in=active_teachers_ids)
        
        return queryset.none()