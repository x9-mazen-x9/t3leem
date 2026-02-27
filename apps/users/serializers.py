from rest_framework import serializers
from rest_framework import serializers
from django.db import transaction
from .models import User
from apps.teachers.models import Teacher
from apps.students.models import Student

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'user_type', 'serial_number']
        read_only_fields = ['serial_number']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True, required=False)
    # حقل إضافي للطالب فقط
    parent_phone = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'password', 'confirm_password', 'password_confirm', 'user_type', 'parent_phone'
        ]

    def validate(self, attrs):
        password = attrs.get('password')
        cp = attrs.get('confirm_password') or attrs.get('password_confirm') or self.initial_data.get('password_confirm')
        if not cp or password != cp:
            raise serializers.ValidationError(
                {"password": "كلمتا المرور غير متطابقتين"}
            )
        attrs['confirm_password'] = cp

        user_type = attrs.get("user_type")

        if user_type == "student":
            if not attrs.get("parent_phone"):
                raise serializers.ValidationError(
                    {"parent_phone": "رقم ولي الأمر مطلوب للطالب."}
                )
            
            # تعديل: منع تطابق رقم الهاتف مع رقم ولي الأمر
            if attrs.get("phone") == attrs.get("parent_phone"):
                raise serializers.ValidationError(
                    {"parent_phone": "رقم ولي الأمر لا يمكن أن يكون نفس رقم هاتف الطالب."}
                )
        
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        parent_phone = validated_data.pop('parent_phone', None)
        user_type = validated_data.get('user_type', 'student')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        if user_type == "teacher":
            Teacher.objects.create(user=user)

        elif user_type == "student":
            Student.objects.create(
                user=user,
                parent_phone=parent_phone,
                date_of_birth="2000-01-01", # قيمة افتراضية أو يمكن طلبها
                phone_number=user.phone
            )

        return user
