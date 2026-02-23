# apps/social/models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.core.models import TenantModel
from apps.users.models import User


class Post(TenantModel):
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='post_records',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField()

    image = models.ImageField(
        upload_to='posts/',
        null=True,
        blank=True,
    )

    share_count = models.PositiveIntegerField(default=0)

    # ---- كاتب المنشور: مدرس أو طالب (واحد فقط) ----
    author_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        db_index=True,
        verbose_name='المدرس الكاتب',
    )
    author_student = models.ForeignKey(
        'students.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        db_index=True,
        verbose_name='الطالب الكاتب',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author_teacher', '-created_at']),
            models.Index(fields=['author_student', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'منشور'
        verbose_name_plural = 'المنشورات'

    def clean(self):
        if self.author_teacher and self.author_student:
            raise ValidationError("يجب أن يكون للمنشور كاتب واحد فقط (مدرس أو طالب).")
        if not self.author_teacher and not self.author_student:
            raise ValidationError("يجب تحديد كاتب للمنشور.")

    def __str__(self):
        return self.title

    @property
    def author_name(self):
        if self.author_teacher:
            return self.author_teacher.user.get_full_name() or self.author_teacher.user.email
        if self.author_student:
            return self.author_student.user.get_full_name() or self.author_student.user.email
        return "مجهول"

    @property
    def author_type(self):
        if self.author_teacher:
            return "teacher"
        if self.author_student:
            return "student"
        return None


class PostLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_likes',
        db_index=True
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_post_like'
            )
        ]
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]


class PostImage(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='images',
        db_index=True
    )
    image = models.ImageField(upload_to='posts/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class SavedPost(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_saved_post'
            )
        ]
        ordering = ['-created_at']
        verbose_name = 'منشور محفوظ'
        verbose_name_plural = 'المنشورات المحفوظة'


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )

    # التعليق يمكن من مدرس أو طالب
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True
    )
    teacher_author = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]
        verbose_name = 'تعليق'
        verbose_name_plural = 'التعليقات'

    @property
    def commenter_name(self):
        if self.student:
            return self.student.user.get_full_name() or self.student.user.email
        if self.teacher_author:
            return self.teacher_author.user.get_full_name() or self.teacher_author.user.email
        return "مجهول"

    @property
    def commenter_type(self):
        if self.student:
            return "student"
        if self.teacher_author:
            return "teacher"
        return None


class Report(models.Model):
    """
    بلاغ على منشور — يرسله أي مستخدم.
    صاحب المنصة يراه في الـ Admin ويقرر.
    """
    REASON_CHOICES = [
        ('spam', 'سبام / إعلانات مزعجة'),
        ('inappropriate', 'محتوى غير لائق'),
        ('harassment', 'تحرش أو إساءة'),
        ('misinformation', 'معلومات مضللة'),
        ('other', 'أخرى'),
    ]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reports',
        db_index=True,
        verbose_name='المنشور'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_sent',
        db_index=True,
        verbose_name='المُبلِّغ'
    )
    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES,
        default='other',
        verbose_name='سبب البلاغ'
    )
    details = models.TextField(
        blank=True,
        verbose_name='تفاصيل إضافية'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False, db_index=True, verbose_name='تم الحل')

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'user'],
                name='unique_report_per_user'
            )
        ]
        verbose_name = 'بلاغ'
        verbose_name_plural = 'البلاغات'

    def __str__(self):
        return f"بلاغ على [{self.post.title}] من [{self.user.email}]"
