from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from apps.core.viewsets import TenantModelViewSet
from apps.core.permissions import IsVerifiedTeacher, IsTeacherOwnerOrReadOnly
from .models import Course, Unit
from .serializers import CourseSerializer, UnitSerializer


class CourseViewSet(TenantModelViewSet):

    queryset = Course.objects.select_related('teacher')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [
                IsAuthenticated(),
                IsTeacherOwnerOrReadOnly(),
                IsVerifiedTeacher(),
            ]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.teacher_profile)


class UnitViewSet(TenantModelViewSet):
    """
    وحدات الكورس: Course → Unit → Lesson
    """
    queryset = Unit.objects.select_related('course', 'teacher')
    serializer_class = UnitSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [
                IsAuthenticated(),
                IsTeacherOwnerOrReadOnly(),
                IsVerifiedTeacher(),
            ]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.teacher_profile)
