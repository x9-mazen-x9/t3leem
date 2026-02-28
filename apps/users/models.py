from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


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
    image = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='صورة البروفايل'
    )

    # ✅ PhoneNumberField — يدعم كل الدول ويتحقق من صحة الرقم
    phone = PhoneNumberField(
        unique=True,
        verbose_name='رقم الهاتف'
    )

    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False)

    serial_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    # لتتبع آخر دخول
    last_login = models.DateTimeField(
        default=timezone.now,
        verbose_name='آخر دخول'
    )

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

    def save(self, *args, **kwargs):
        if not self.serial_number:
            from django.utils.crypto import get_random_string
            from django.db import IntegrityError as _IntegrityError

            base_prefix = "TCH-" if self.user_type == 'teacher' else "STU-"

            # توليد serial آمن بدون race condition
            for _ in range(10):
                self.serial_number = base_prefix + get_random_string(
                    6, allowed_chars="0123456789"
                )
                try:
                    super().save(*args, **kwargs)
                    return
                except _IntegrityError:
                    self.serial_number = ""
                    continue

            raise RuntimeError(
                "تعذّر توليد serial_number فريد بعد 10 محاولات."
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'