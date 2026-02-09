# apps/lessons/models.py
from django.db import models
from apps.core.models import TenantModel

class Lesson(TenantModel):
    """
    نموذج الدرس: يرث من TenantModel لضمان وجود حقل 'teacher'.
    """
    title = models.CharField(max_length=200, verbose_name='عنوان الدرس')
    description = models.TextField(blank=True, verbose_name='وصف الدرس')
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')
    
    # Bunny Stream Integration
    # نخزن GUID الخاص بالفيديو وليس الرابط المباشر لأغراض الأمان
    bunny_video_id = models.CharField(max_length=255, blank=True, null=True, help_text="معرف الفيديو من Bunny Stream")
    bunny_library_id = models.CharField(max_length=255, blank=True, null=True, help_text="معرف المكتبة من Bunny Stream")
    
    # ملفات الـ PDF (تخزين عبر Bunny Object Storage)
    lesson_material = models.FileField(
        upload_to='lesson_materials/%Y/%m/', 
        blank=True, 
        null=True, 
        verbose_name='ملف الدرس (PDF)',
        # سيتم ضبط التخزين في settings.py ليستخدم bunny
    )

    is_published = models.BooleanField(default=False, verbose_name='منشور')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'الدروس'
        ordering = ['order', '-created_at']