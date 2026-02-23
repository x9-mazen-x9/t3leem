from django.db import models
from django.db.models import Avg
from apps.core.models import TenantModel
from apps.courses.models import Course
from django.conf import settings


class Lesson(TenantModel):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    unit = models.ForeignKey(
        'courses.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name='الوحدة الدراسية',
    )

    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0, db_index=True)

    bunny_video_id = models.CharField(max_length=255, blank=True, null=True)

    lesson_material = models.FileField(
        upload_to='lesson_materials/%Y/%m/',
        blank=True,
        null=True,
    )

    # ===========================
    # Access Control Fields
    # ===========================

    is_trial = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='حصة تجريبية',
        help_text='أي شخص يمكنه مشاهدة هذه الحصة بدون اشتراك',
    )

    is_force_open = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='فتح إجباري',
        help_text='يفتح هذا الدرس حتى لو الدروس السابقة لم تكتمل (مثلاً درس مراجعة)',
    )

    publish_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ النشر',
        help_text='إذا كان محدداً، لن يظهر الدرس قبل هذا التاريخ',
    )

    # ===========================
    # Homework Field
    # ===========================

    has_homework = models.BooleanField(
        default=False,
        verbose_name='يحتوي على واجب',
    )

    is_published = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['course', 'is_published']),
            models.Index(fields=['course', 'order']),
            models.Index(fields=['course', 'is_trial']),
            models.Index(fields=['course', 'is_force_open']),
        ]

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg('rating')).get('avg') or 0

    @property
    def embed_url(self):
        if self.bunny_video_id:
            return f"https://iframe.mediadelivery.net/embed/{settings.BUNNY_STREAM_LIBRARY_ID}/{self.bunny_video_id}"
        return None
