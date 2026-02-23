# apps/core/permissions.py
from rest_framework import permissions
from django.utils import timezone


class IsTeacherOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not hasattr(request.user, "teacher_profile"):
            return False

        teacher = request.user.teacher_profile

        if hasattr(obj, "teacher"):
            return obj.teacher == teacher

        if hasattr(obj, "created_by"):
            return obj.created_by == teacher

        return False


class IsStudentOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            hasattr(request.user, "student_profile") and
            obj.student.user == request.user
        )

class IsVerifiedTeacher(permissions.BasePermission):
    """
    نقطة 13: يمنع المدرس المجمد (منتهي الاشتراك) من أي فعالية
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not hasattr(user, "teacher_profile"):
            return False

        profile = user.teacher_profile
        today = timezone.now().date()

        # يجب أن يكون لديه اشتراك ساري
        has_valid_subscription = (
            profile.subscription_expiry is not None and
            profile.subscription_expiry >= today
        )
        return has_valid_subscription

# باقي الصلاحيات تظل كما هي
class IsActiveTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not hasattr(user, "teacher_profile"):
            return True

        profile = user.teacher_profile
        today = timezone.now().date()

        return (
            profile.subscription_expiry is not None and
            profile.subscription_expiry >= today
        )


class IsPlatformOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_superuser
        )


class CanCreatePost(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method not in ('POST',):
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if hasattr(user, 'student_profile'):
            return True
        if hasattr(user, 'teacher_profile'):
            profile = user.teacher_profile
            today = timezone.now().date()
            return (
                profile.subscription_expiry is not None and
                profile.subscription_expiry >= today
            )
        return False
