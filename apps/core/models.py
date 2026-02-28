from django.db import models
from django.conf import settings

class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantModel(TimeStampedModel):
    teacher = models.ForeignKey(
        'teachers.Teacher', 
        on_delete=models.CASCADE, 
        related_name='%(class)s_records',
        help_text="المالك الأساسي لهذا السجل"
    )

    class Meta:
        abstract = True


class ActivityLog(models.Model):
    """
    سجل نشاط يسجل آخر العمليات التي قام بها المستخدم.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='activity_logs'
    )
    action = models.CharField(max_length=255, verbose_name='الحدث/النشاط')
    description = models.TextField(blank=True, verbose_name='الوصف/تفاصيل')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'سجل النشاط'
        verbose_name_plural = 'سجلات النشاط'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.action}"
