# apps/social/serializers.py
from rest_framework import serializers
from .models import Post, Comment
from apps.users.serializers import TeacherMiniSerializer


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user_name', 'created_at']

    def get_user_name(self, obj):
        return obj.student.user.email


class PostSerializer(serializers.ModelSerializer):
    teacher = TeacherMiniSerializer(source='created_by', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'image',
            'created_at',
            'teacher',
            'comments'
        ]
        read_only_fields = ['teacher', 'created_at']
