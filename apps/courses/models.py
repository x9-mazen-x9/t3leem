from django.db import models
from apps.core.models import TenantModel
from apps.teachers.models import Teacher

class Course(TenantModel):
    ACCESS_FREE = 'FREE'
    ACCESS_SEQUENTIAL = 'SEQUENTIAL'
    ACCESS_TYPE_CHOICES = [
        (ACCESS_FREE, 'مجاني (كل الدروس متاحة)'),
        (ACCESS_SEQUENTIAL, 'تسلسلي (يفتح درس درس)'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # نقطة 6: صورة الغلاف
    cover_image = models.ImageField(
        upload_to='course_covers/', 
        null=True, 
        blank=True, 
        verbose_name="صورة الغلاف"
    )

    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPE_CHOICES,
        default=ACCESS_FREE,
        db_index=True,
        verbose_name='نوع الوصول',
    )

    has_trial = models.BooleanField(default=False, verbose_name='يحتوي على حصة تجريبية')
    is_published = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.teacher.user.get_full_name()}"


class Unit(TenantModel):
    """
    الوحدة الدراسية: تجمع مجموعة من الدروس داخل الكورس.
    Course → Unit → Lesson
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='units',
        db_index=True,
    )

    title = models.CharField(max_length=255, verbose_name='عنوان الوحدة')

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name='الترتيب',
    )

    has_unit_exam = models.BooleanField(
        default=False,
        verbose_name='تحتوي على امتحان وحدة',
    )

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')
        indexes = [
            models.Index(fields=['course', 'order']),
        ]
        verbose_name = 'وحدة دراسية'
        verbose_name_plural = 'الوحدات الدراسية'

    def __str__(self):
        return f"{self.course.title} - {self.title}"
