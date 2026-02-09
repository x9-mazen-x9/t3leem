from django.db import models
from apps.users.models import User

class Teacher(models.Model):
    """
    نموذج المدرس: يحتوي على بيانات المدرس الإضافية وحساب البوني للمقاطعة (Revenue).
    يرتبط بنموذج User واحد.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='السيرة الذاتية')
    website_url = models.URLField(blank=True, verbose_name='الموقع الإلكتروني')
    
    # إعدادات Bunny Stream للدفع
    bunny_stream_api_key = models.CharField(max_length=255, blank=True, null=True, help_text="مفتاح API للبث")
    bunny_storage_api_key = models.CharField(max_length=255, blank=True, null=True, help_text="مفتاح API للتخزين")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"المدرس: {self.user.get_full_name()}"

    class Meta:
        verbose_name = 'مدرس'
        verbose_name_plural = 'المدرسين'

class Partner(models.Model):
    """
    نموذج الشركاء: إذا كان للمدرس شركاء في الأرباح.
    """
    name = models.CharField(max_length=100, verbose_name='اسم الشريك')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    revenue_share_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='نسبة الأرباح')
    
    # هذا الشريك تابع لمدرس محدد (Multi-tenancy)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='partners')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'شريك'
        verbose_name_plural = 'الشركاء'