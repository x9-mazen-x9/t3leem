from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('البريد الإلكتروني مطلوب')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    first_name = models.CharField(max_length=30, verbose_name='الاسم الأول')
    last_name = models.CharField(max_length=30, verbose_name='اسم العائلة')

    phone_regex = RegexValidator(
        regex=r'^01[0-9]{9}$',
        message="رقم الهاتف يجب أن يكون رقم مصري صحيح."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=11,
        unique=True,
        verbose_name='رقم الهاتف'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # لتتبع آخر دخول (نقطة 22)
    last_login = models.DateTimeField(default=timezone.now, verbose_name='آخر دخول')

    USER_TYPE_CHOICES = (
        ('teacher', 'مدرس'),
        ('student', 'طالب'),
    )

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
        db_index=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'