"""
Progress Engine: محرك التقدم
يتتبع تقدم الطالب في كل درس (مشاهدة + واجب = إتمام الدرس).
"""
from django.db import models
from apps.students.models import Student
from apps.lessons.models import Lesson


class LessonProgress(models.Model):
    """
    سجل تقدم الطالب في درس معين.
    lesson_completed = video_completed AND homework_submitted
    """

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        db_index=True,
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress_records',
        db_index=True,
    )

    # ─── Video Progress ───────────────────────────────────────────
    watched_percentage = models.FloatField(
        default=0.0,
        verbose_name='نسبة المشاهدة (%)',
    )

    last_second = models.PositiveIntegerField(
        default=0,
        verbose_name='آخر ثانية وصل إليها',
    )

    video_completed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='الفيديو مكتمل (100%)',
    )

    # ─── Homework ─────────────────────────────────────────────────
    homework_submitted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='الواجب مسلّم',
    )

    homework_graded = models.BooleanField(
        default=False,
        verbose_name='الواجب متصحح',
    )

    # ─── Completion ───────────────────────────────────────────────
    lesson_completed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='الدرس مكتمل',
        help_text='يصبح True تلقائياً عند video_completed AND homework_submitted',
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lesson')
        ordering = ['lesson__order']
        indexes = [
            models.Index(fields=['student', 'lesson']),
            models.Index(fields=['student', 'lesson_completed']),
        ]
        verbose_name = 'تقدم الدرس'
        verbose_name_plural = 'تقدم الدروس'

    def __str__(self):
        return (
            f"{self.student.user.get_full_name()} → "
            f"{self.lesson.title} ({self.watched_percentage:.0f}%)"
        )

    def save(self, *args, **kwargs):
        # Compute lesson_completed: video done AND (no homework OR homework submitted)
        if self.lesson.has_homework:
            self.lesson_completed = self.video_completed and self.homework_submitted
        else:
            self.lesson_completed = self.video_completed
        super().save(*args, **kwargs)
