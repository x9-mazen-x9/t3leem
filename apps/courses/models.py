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


class ActivationCode(models.Model):
    """
    كود تفعيل يُنشئه المدرس ويستخدمه الطالب للاشتراك في الكورس.
    - الكود من 10 خانات (أرقام + حروف + رموز).
    - كل كود يُستخدم مرة واحدة فقط، وبعدها تنتهي صلاحيته نهائياً.
    """
    ALLOWED_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789@#$%&'

    code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        verbose_name='كود التفعيل',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='activation_codes',
        verbose_name='الكورس',
    )
    created_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='created_codes',
        verbose_name='المدرس',
    )

    # Single-use enforcement
    is_used = models.BooleanField(default=False, db_index=True, verbose_name='مستخدم')
    used_by = models.ForeignKey(
        'students.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='redeemed_codes',
        verbose_name='الطالب المستخدم',
    )
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='وقت الاستخدام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='وقت الإنشاء')

    class Meta:
        verbose_name = 'كود تفعيل'
        verbose_name_plural = 'أكواد التفعيل'
        indexes = [
            models.Index(fields=['course', 'is_used']),
            models.Index(fields=['created_by', 'course']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({'مستخدم' if self.is_used else 'جديد'}) - {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.code:
            from django.utils.crypto import get_random_string
            from django.db import IntegrityError as _IntegrityError

            # نُولّد الكود ونحاول الحفظ مباشرةً — يمنع race condition تماماً
            for _ in range(10):
                self.code = get_random_string(10, allowed_chars=self.ALLOWED_CHARS)
                try:
                    super().save(*args, **kwargs)
                    return  # نجح الحفظ
                except _IntegrityError:
                    self.code = ""  # كوّن كوداً آخر
                    continue
            raise RuntimeError("تعذّر توليد كود تفعيل فريد بعد 10 محاولات.")
        super().save(*args, **kwargs)
