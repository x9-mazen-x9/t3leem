from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from apps.teachers.models import Teacher, Follow, ServiceRequest


@receiver(post_save, sender=Teacher)
def create_teacher_group(sender, instance: Teacher, created, **kwargs):
    """
    إنشاء مجموعة خاصة تلقائياً لكل مدرس جديد.
    """
    if created:
        from apps.teachers.models import TeacherGroup
        TeacherGroup.objects.get_or_create(teacher=instance)


@receiver(post_save, sender=Follow)
def auto_verify_on_followers(sender, instance: Follow, created, **kwargs):
    """
    التحقق التلقائي إذا وصل عدد المتابعين إلى 5000.
    """
    if created:
        teacher = instance.teacher
        followers_count = teacher.followers.count()
        if followers_count >= 5000 and not teacher.is_verified:
            teacher.is_verified = True
            teacher.save(update_fields=['is_verified'])


@receiver(post_save, sender=ServiceRequest)
def activate_service_on_request(sender, instance: ServiceRequest, created, **kwargs):
    """
    عند تفعيل الطلب بواسطة المشرف:
    - يبدأ العد التنازلي لـ ٣١ يوماً
    - يتم تفعيل مزايا المدرس (شارة/أولوية)
    """
    if instance.status == 'active':
        # تعيين وقت التفعيل والإنتهاء إن لم تكن محددة
        if not instance.activated_at:
            instance.activated_at = timezone.now()
        if not instance.expiry_date:
            duration = instance.service.duration_days or 31
            instance.expiry_date = (instance.activated_at.date() + timedelta(days=duration))
        instance.save(update_fields=['activated_at', 'expiry_date'])

        code = instance.service.code.lower()
        teacher = instance.teacher
        if 'verify' in code:
            teacher.is_verified = True
            teacher.save(update_fields=['is_verified'])
        if 'priority' in code:
            teacher.priority_service = True
            teacher.save(update_fields=['priority_service'])
