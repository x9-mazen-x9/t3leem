from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from apps.core.viewsets import TenantModelViewSet
from apps.core.permissions import (
    IsTeacherOwnerOrReadOnly,
    IsVerifiedTeacher
)
from .models import Lesson
from .serializers import LessonSerializer, LessonListSerializer
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
                publish_date__isnull=True
            ) | qs.filter(
                is_published=True,
                publish_date__lte=today
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

        video_id = create_bunny_video(lesson.title)
        lesson.bunny_video_id = video_id
        lesson.save(update_fields=["bunny_video_id"])

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
