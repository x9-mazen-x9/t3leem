from rest_framework import serializers
from .models import Course, Unit

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "course", "title", "order", "has_unit_exam", "created_at"]

class CourseSerializer(serializers.ModelSerializer):
    units_count = serializers.SerializerMethodField()
    teacher_contact_numbers = serializers.JSONField(source='teacher.contact_numbers', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "title", "description", "price", 
            "cover_image", # صورة الغلاف
            "access_type", "has_trial", "is_published", 
            "units_count", "created_at",
            "teacher_contact_numbers", # أرقام التواصل
            "teacher_name"
        ]

    def get_units_count(self, obj):
        return obj.units.count()