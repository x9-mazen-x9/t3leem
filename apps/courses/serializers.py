from rest_framework import serializers
from .models import Course, Unit, ActivationCode


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
            "cover_image",
            "access_type", "has_trial", "is_published",
            "units_count", "created_at",
            "teacher_contact_numbers",
            "teacher_name"
        ]

    def get_units_count(self, obj):
        return getattr(obj, 'units_count', obj.units.count())


class UnitWithLessonsSerializer(serializers.ModelSerializer):
    """وحدة مع قائمة دروسها — للـ Course Detail Page."""
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ["id", "title", "order", "has_unit_exam", "lessons"]

    def get_lessons(self, obj):
        from apps.lessons.serializers import LessonListSerializer
        lessons = obj.lessons.filter(is_published=True).order_by('order')
        return LessonListSerializer(lessons, many=True, context=self.context).data


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    تفاصيل الكورس الكاملة لصفحة التفاصيل — مع الوحدات والأستاذ وأرقام التواصل.
    """
    teacher_id = serializers.IntegerField(source='teacher.id', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    teacher_image = serializers.SerializerMethodField()
    teacher_contact_numbers = serializers.JSONField(source='teacher.contact_numbers', read_only=True)
    teacher_is_verified = serializers.BooleanField(source='teacher.is_verified', read_only=True)
    units = serializers.SerializerMethodField()
    units_count = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id", "title", "description", "price", "cover_image",
            "access_type", "has_trial", "is_published", "created_at",
            "teacher_id", "teacher_name", "teacher_image",
            "teacher_contact_numbers", "teacher_is_verified",
            "units", "units_count", "lessons_count",
        ]

    def get_teacher_image(self, obj):
        user = obj.teacher.user
        try:
            return user.image.url if user.image else None
        except Exception:
            return None

    def get_units(self, obj):
        units = obj.units.order_by('order')
        return UnitWithLessonsSerializer(units, many=True, context=self.context).data

    def get_units_count(self, obj):
        return getattr(obj, 'units_count', obj.units.count())

    def get_lessons_count(self, obj):
        return obj.lessons.filter(is_published=True).count()


class ActivationCodeSerializer(serializers.ModelSerializer):
    """عرض كود التفعيل للمدرس مع حالته."""
    used_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ActivationCode
        fields = [
            "id", "code", "is_used",
            "used_by_name", "used_at", "created_at",
        ]
        read_only_fields = fields

    def get_used_by_name(self, obj):
        if obj.used_by:
            return obj.used_by.user.get_full_name()
        return None

