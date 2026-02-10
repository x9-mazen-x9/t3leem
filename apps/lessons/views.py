# ---------------------------------------------------------------------

# apps/lessons/views.py
from rest_framework import viewsets
from .models import Lesson
from .serializers import LessonSerializer
from apps.core.viewsets import TenantModelViewSet
from apps.core.permissions import IsTeacherOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated


class LessonViewSet(TenantModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
    # تطبيق الصلاحيات الخاصة: المدرس يعدل اللي هو مالكه، الباقي يقرأ فقط
    permission_classes = [IsAuthenticated, IsTeacherOwnerOrReadOnly]

