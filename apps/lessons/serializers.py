# apps/lessons/serializers.py
from rest_framework import serializers
from .models import Lesson
from apps.users.serializers import TeacherMiniSerializer
from .utils import generate_bunny_signed_url

class LessonSerializer(serializers.ModelSerializer):
    teacher = TeacherMiniSerializer(read_only=True)
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'bunny_video_id', 'video_url', 'lesson_material', 'created_at', 'teacher']
        read_only_fields = ['teacher', 'created_at']

    def get_video_url(self, obj):
        if obj.bunny_video_id:
            return generate_bunny_signed_url(obj.bunny_video_id)
        return None