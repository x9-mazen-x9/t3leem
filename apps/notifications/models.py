from django.db import models
from django.conf import settings


class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ('post', 'منشور جديد'),
        ('comment', 'تعليق جديد'),
        ('like', 'إعجاب بمنشور'),
        ('expiry', 'انتهاء الاشتراك'),
        ('subscription_expired', 'اشتراك منتهي'),
        ('broadcast', 'رسالة جماعية'),
        ('system', 'تنبيه نظام'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default='system',
        db_index=True
    )

    is_read = models.BooleanField(default=False, db_index=True)

    link = models.CharField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'notification_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user_id}"
