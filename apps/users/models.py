from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

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
    last_name = models.CharField(max_length=30, verbose_name='الاسم الأخير')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 

    USER_TYPE_CHOICES = (
        ('admin', 'مدير النظام'),
        ('teacher', 'مدرس'),
        ('student', 'طالب'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # ✅ التعديل الأول: إضافة دالة get_full_name يدوياً لأننا ورثنا من AbstractBaseUser
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'