from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from apps.core.viewsets import TenantModelViewSet
from apps.core.permissions import (
    IsTeacherOwnerOrReadOnly,
    IsVerifiedTeacher
)
from .models import Lesson
from .serializers import LessonSerializer, LessonListSerializer
from apps.core.utils import log_activity
from .services import get_unlocked_lessons_for_student
from .bunny import create_bunny_video


class LessonViewSet(TenantModelViewSet):

    queryset = Lesson.objects.select_related("course", "teacher", "unit")
    serializer_class = LessonSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return LessonListSerializer
        return LessonSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        today = timezone.now().date()
        # لا تُظهر الدروس التي لم يحن تاريخ نشرها بعد (لغير الـ owner)
        user = self.request.user
        if not hasattr(user, 'teacher_profile'):
            qs = qs.filter(
                is_published=True
            ).filter(
                Q(publish_date__isnull=True) | Q(publish_date__lte=today)
            )
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [
                IsAuthenticated(),
                IsTeacherOwnerOrReadOnly(),
                IsVerifiedTeacher(),
            ]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        teacher = self.request.user.teacher_profile
        lesson = serializer.save(teacher=teacher)
        
        log_activity(
            user=self.request.user,
            action="أنشأ درس",
            description=f"أنشأ درس جديد: {lesson.title}"
        )
        
        try:
            from .tasks import create_bunny_video_task
            create_bunny_video_task.delay(lesson.id, lesson.title)
        except Exception:
            pass
    @action(detail=False, methods=['get'], url_path='unlocked/(?P<course_id>[^/.]+)')
    def unlocked(self, request, course_id=None):
        """
        GET /api/lessons/unlocked/{course_id}/
        يعيد IDs الدروس المفتوحة للطالب في الكورس.
        """
        if not hasattr(request.user, 'student_profile'):
            return Response({'detail': 'فقط الطلاب.'}, status=403)

        from apps.courses.models import Course
        from django.shortcuts import get_object_or_404

        course = get_object_or_404(Course, pk=course_id)
        student = request.user.student_profile
        unlocked_ids = get_unlocked_lessons_for_student(student, course)
        return Response({'unlocked_lesson_ids': unlocked_ids})
