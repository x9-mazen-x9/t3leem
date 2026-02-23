from rest_framework import serializers
from apps.teachers.models import Teacher


class TeacherMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    follower_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id",
            "full_name",
            "email",
            "bio",
            "is_verified",
            "priority_service",
            "follower_count",
        ]
