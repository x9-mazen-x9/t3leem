
# ---------------------------------------------------------------------

# apps/social/views.py
from rest_framework import viewsets
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from apps.core.viewsets import TenantModelViewSet
from apps.core.permissions import IsTeacherOwnerOrReadOnly, IsStudentOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated


class PostViewSet(TenantModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsTeacherOwnerOrReadOnly]

class CommentViewSet(viewsets.ModelViewSet):
    # التعليقات قد تحتاج فلترة مختلفة قليلاً (ترتبط بالبوستات التي يراها الطالب)
    # لكن لتبسيط الأمر، سنفترض أنها تتبع نظام الـ Tenant أيضاً
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsStudentOwnerOrReadOnly()]
        return [IsAuthenticated()] 
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        # فلترة التعليقات لتظهر فقط تلك التي تنتمي للـ Tenant (المدرس) الخاص بالمستخدم
        if hasattr(user, 'teacher_profile'):
            return qs.filter(post__teacher=user.teacher_profile)
        elif hasattr(user, 'student_profile'):
            return qs.filter(post__teacher=user.student_profile.teacher)
        return qs.none()
    
    def perform_create(self, serializer):
        # ربط التعليق بالمستخدم الحالي تلقائياً
        serializer.save(user=self.request.user)