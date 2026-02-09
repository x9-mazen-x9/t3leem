# apps/social/models.py
from django.db import models
from apps.core.models import TenantModel
from apps.students.models import Student

class Post(TenantModel):

    title = models.CharField(max_length=200, verbose_name='عنوان المنشور')
    content = models.TextField(verbose_name='محتوى المنشور')
    created_by = models.ForeignKey(
        'teachers.Teacher', 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='تم النشر بواسطة'
    )

    def __str__(self):
        return f"{self.title} - {self.teacher.user.email}"

    class Meta:
        verbose_name = 'منشور'
        verbose_name_plural = 'المنشورات'
        ordering = ['-created_at']

class Comment(models.Model):
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='الطالب')
    content = models.TextField(verbose_name='نص التعليق')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"تعليق بواسطة {self.student.user.email}"

    class Meta:
        verbose_name = 'تعليق'
        verbose_name_plural = 'التعليقات'
        ordering = ['-created_at']