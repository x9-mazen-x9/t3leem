from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.users.models import User
from apps.courses.models import Course
from datetime import timedelta
from django.conf import settings

class Student(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    date_of_birth = models.DateField(null=False, blank=False)
    phone_number = models.CharField(max_length=20, blank=False, null=False)
    parent_phone = models.CharField(max_length=20, blank=False, null=False)

    serial_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.serial_number:
            base_prefix = "STU-"
            from django.utils.crypto import get_random_string

            while True:
                candidate = base_prefix + get_random_string(
                    6, allowed_chars="0123456789"
                )
                if not Student.objects.filter(serial_number=candidate).exists():
                    self.serial_number = candidate
                    break

        super().save(*args, **kwargs)


class Enrollment(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    phone_number = models.CharField(max_length=20, blank=False, null=False)
    parent_phone = models.CharField(max_length=20, blank=False, null=False)

    is_active = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)

    start_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
        indexes = [
            models.Index(fields=["student", "course"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.student.user.email} -> {self.course.title}"

    def clean(self):
        if self.is_active and self.is_pending:
            raise ValidationError(
                "Enrollment cannot be active and pending at the same time."
            )

    @property
    def is_expired(self):
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()

    @property
    def is_valid_for_access(self):
        if not self.is_active or self.is_pending:
            return False
        return not self.is_expired
    
    def activate(self):
        today = timezone.now().date()

        # لو الاشتراك كان منتهي
        if self.expiry_date and self.expiry_date < today:
            start = today
        else:
            # لو بيجدد قبل ما ينتهي
            start = self.expiry_date or today

        self.start_date = today
        self.expiry_date = start + timedelta(
            days=settings.COURSE_SUBSCRIPTION_DAYS
        )

        self.is_active = True
        self.is_pending = False
        self.save(update_fields=[
            "start_date",
            "expiry_date",
            "is_active",
            "is_pending"
        ])