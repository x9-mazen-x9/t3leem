# apps/users/serializers.py
from rest_framework import serializers
from .models import User
from apps.teachers.models import Teacher

class TeacherMiniSerializer(serializers.ModelSerializer):
    """للاستخدام داخل الـ Nested Serializer"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'bio']

    def get_full_name(self, obj):
        return obj.user.get_full_name()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # ✅ التعديل الثاني: استبدل is_student/is_teacher بـ user_type
        fields = ['id', 'email', 'first_name', 'last_name', 'user_type']