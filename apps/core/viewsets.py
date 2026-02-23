# apps/core/viewsets.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q


class TenantModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet يطبق عزل البيانات بناءً على الاشتراكات الفعالة.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # المدرس يرى محتواه فقط
        if hasattr(user, "teacher_profile"):
            return queryset.filter(teacher=user.teacher_profile)

        # الطالب يرى فقط المحتوى المرتبط بالكورسات التي لديه اشتراك صالح بها
        elif hasattr(user, "student_profile"):
            from apps.students.models import Enrollment

            today = timezone.now().date()

            active_courses_ids = (
                user.student_profile.enrollments
                .filter(
                    is_active=True,
                    is_pending=False,
                )
                .filter(
                    Q(expiry_date__isnull=True) | Q(expiry_date__gte=today)
                )
                .values_list("course_id", flat=True)
            )

            # لو الموديل فيه course (زي Lesson)
            if hasattr(queryset.model, "course"):
                return queryset.filter(course_id__in=active_courses_ids)

            # لو الموديل مربوط مباشرة بالمدرس (زي Post)
            if hasattr(queryset.model, "teacher"):
                return queryset.filter(
                    teacher__courses__id__in=active_courses_ids
                ).distinct()

        return queryset.none()
