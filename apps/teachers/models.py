from django.db import models
from apps.users.models import User
from django.db.models import Avg
from django.contrib.postgres.fields import ArrayField # لو PostgreSQL

# لو مش PostgreSQL نستخدم TextField ونحفظ JSON
from django.db.models import TextField

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='السيرة الذاتية')
    
    # نقطة 6: أرقام التواصل للظهور أعلى صفحة الكورسات
    contact_numbers = models.JSONField(
        default=list, 
        blank=True, 
        verbose_name="أرقام التواصل للإعلان",
        help_text="قائمة بأرقام الواتس اب لتظهر للطلاب"
    )

    is_verified = models.BooleanField(default=False, verbose_name='حساب موثق')
    subscription_expiry = models.DateField(null=True, blank=True, verbose_name='تاريخ انتهاء الاشتراك')
    
    is_verified_paid = models.BooleanField(default=False, verbose_name='توثيق مدفوع')
    is_verified_auto = models.BooleanField(default=False, verbose_name='توثيق تلقائي (5000 متابع)')
    priority_service = models.BooleanField(default=False, verbose_name='خدمة أولوية البحث')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"المدرس: {self.user.get_full_name()}"

    class Meta:
        verbose_name = 'مدرس'
        verbose_name_plural = 'المدرسين'

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg('rating')).get('avg') or 0

    @property
    def followers_count(self):
        return self.followers.count()


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

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follows', db_index=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='followers', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'teacher'], name='unique_follow')
        ]
        indexes = [
            models.Index(fields=['teacher', '-created_at']),
        ]


class Service(models.Model):
    """
    متجر خدمات المدرس (تحقق - شارة، أولوية البحث).
    الأسعار بالعملة EGP.
    """
    code = models.CharField(max_length=50, unique=True, verbose_name='كود الخدمة')
    name = models.CharField(max_length=100, verbose_name='اسم الخدمة')
    price_egp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='السعر (EGP)')
    duration_days = models.PositiveIntegerField(default=31, verbose_name='مدة الخدمة بالأيام')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'خدمة'
        verbose_name_plural = 'الخدمات'

    def __str__(self):
        return self.name

class TeacherServicePurchase(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='service_purchases')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='purchases')
    start_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'شراء خدمة'
        verbose_name_plural = 'مشتريات الخدمات'

    def __str__(self):
        return f"{self.teacher_id} - {self.service.code}"

class ServiceRequest(models.Model):
    """
    طلب خدمة يقدمه المدرس ويتم تفعيله يدوياً بواسطة مالك المنصة.
    """
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('active', 'مفعّل'),
        ('rejected', 'مرفوض'),
    )
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='service_requests')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = 'طلب خدمة'
        verbose_name_plural = 'طلبات الخدمات'
        ordering = ['-requested_at']

    def __str__(self):
        return f"طلب {self.service.code} لـ {self.teacher_id} ({self.status})"

class TeacherReview(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='reviews', db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_reviews')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['teacher', '-created_at']),
        ]


class Complaint(models.Model):
    """
    شكاوى الطلاب ضد المدرسين.
    """
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='complaints')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='complaints')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'شكوى'
        verbose_name_plural = 'الشكاوى'

class TeacherGroup(models.Model):
    """
    مجموعة خاصة للمدرس تضم الطلاب الحاليين والسابقين.
    """
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='group')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مجموعة المدرس'
        verbose_name_plural = 'مجموعات المدرسين'

class TeacherGroupMember(models.Model):
    group = models.ForeignKey(TeacherGroup, on_delete=models.CASCADE, related_name='members')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    class Meta:
        unique_together = ('group', 'student')
        verbose_name = 'عضو مجموعة'
        verbose_name_plural = 'أعضاء المجموعات'
