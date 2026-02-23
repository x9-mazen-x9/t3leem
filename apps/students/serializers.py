from rest_framework import serializers
from apps.students.models import Student
from .models import Enrollment


class StudentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "serial_number",
            "date_of_birth",
            "phone_number",
            "parent_phone",
        ]





class EnrollmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ["is_active", "is_pending", "enrolled_at"]
