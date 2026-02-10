# apps/users/serializers.py
from rest_framework import serializers
from .models import User
from apps.teachers.models import Teacher

class TeacherMiniSerializer(serializers.ModelSerializer):
    """للاستخدام داخل الـ Nested Serializer"""
    full_name = serializers.SerializerMethodField()
    image = serializers.ImageField(source='profile_image')

    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'image', 'bio']

    def get_full_name(self, obj):
        return obj.user.get_full_name()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_student', 'is_teacher']