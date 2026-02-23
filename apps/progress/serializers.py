from rest_framework import serializers
from .models import LessonProgress


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    has_homework = serializers.BooleanField(source='lesson.has_homework', read_only=True)

    class Meta:
        model = LessonProgress
        fields = [
            'id',
            'lesson',
            'lesson_title',
            'has_homework',
            'watched_percentage',
            'last_second',
            'video_completed',
            'homework_submitted',
            'homework_graded',
            'lesson_completed',
            'updated_at',
        ]
        read_only_fields = [
            'video_completed',
            'lesson_completed',
            'homework_graded',
            'updated_at',
        ]


class SaveProgressSerializer(serializers.Serializer):
    """Used by the save-progress endpoint."""
    lesson_id = serializers.IntegerField()
    last_second = serializers.IntegerField(min_value=0)
    total_seconds = serializers.IntegerField(min_value=1)
