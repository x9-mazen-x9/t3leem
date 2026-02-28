"""
محرك التقدم - Views
- save_progress: تحفظ last_second وتحسب watched_percentage وتضع video_completed لو 100%
- submit_homework: تعيين homework_submitted = True
- list: عرض تقدم الطالب في كل الدروس
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.lessons.models import Lesson
from apps.lessons.services import user_can_access_lesson
from .models import LessonProgress
from .serializers import LessonProgressSerializer, SaveProgressSerializer


class LessonProgressViewSet(viewsets.GenericViewSet):
    """
    ViewSet لمتابعة تقدم الطالب.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LessonProgressSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            return LessonProgress.objects.none()
        return (
            LessonProgress.objects
            .filter(student=user.student_profile)
            .select_related('lesson', 'lesson__course')
        )

    def list(self, request):
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = LessonProgressSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = LessonProgressSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='save')
    def save_progress(self, request):
        """
        POST /api/progress/save/
        Body: { lesson_id, last_second, total_seconds }
        يحفظ التقدم ويحسب watched_percentage تلقائياً.
        """
        serializer = SaveProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        lesson = get_object_or_404(Lesson, pk=data['lesson_id'])

        # تحقق من أحقية الوصول
        if not user_can_access_lesson(request.user, lesson):
            return Response(
                {'detail': 'لا يمكنك الوصول لهذا الدرس.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'detail': 'فقط الطلاب يمكنهم حفظ التقدم.'},
                status=status.HTTP_403_FORBIDDEN
            )

        student = request.user.student_profile

        # احسب النسبة
        last_second = data['last_second']
        total_seconds = data['total_seconds']
        percentage = min((last_second / total_seconds) * 100, 100.0)
        video_completed = percentage >= 100.0

        progress, created = LessonProgress.objects.get_or_create(
            student=student,
            lesson=lesson,
            defaults={
                'last_second': last_second,
                'watched_percentage': percentage,
                'video_completed': video_completed,
            }
        )

        if not created:
            # فقط نحدّث لو التقدم الجديد أكبر من القديم
            if last_second > progress.last_second:
                progress.last_second = last_second
                progress.watched_percentage = percentage
                if video_completed:
                    progress.video_completed = True
                progress.save()

        return Response(LessonProgressSerializer(progress).data)

    @action(detail=False, methods=['post'], url_path='submit-homework')
    def submit_homework(self, request):
        """
        POST /api/progress/submit-homework/
        Body: { lesson_id }
        يسجل تسليم الواجب ويحسب lesson_completed تلقائياً.
        """
        lesson_id = request.data.get('lesson_id')
        if not lesson_id:
            return Response(
                {'detail': 'lesson_id مطلوب.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        lesson = get_object_or_404(Lesson, pk=lesson_id)

        if not lesson.has_homework:
            return Response(
                {'detail': 'هذا الدرس لا يحتوي على واجب.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'detail': 'فقط الطلاب يمكنهم تسليم الواجبات.'},
                status=status.HTTP_403_FORBIDDEN
            )

        student = request.user.student_profile

        progress, _ = LessonProgress.objects.get_or_create(
            student=student,
            lesson=lesson,
        )

        progress.homework_submitted = True
        progress.save()  # lesson_completed يُحسب تلقائياً في save()

        return Response(LessonProgressSerializer(progress).data)

    @action(detail=False, methods=['get'], url_path='course/(?P<course_id>[^/.]+)')
    def course_progress(self, request, course_id=None):
        """
        GET /api/progress/course/{course_id}/
        يعرض تقدم الطالب في كل دروس كورس معين.
        """
        qs = self.get_queryset().filter(lesson__course_id=course_id)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = LessonProgressSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = LessonProgressSerializer(qs, many=True)
        return Response(serializer.data)
