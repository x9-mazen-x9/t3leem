from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.teachers.models import Teacher
from apps.notifications.models import Notification

@shared_task
def check_teacher_subscriptions():
    """
    مهمة دورية للتحقق من اشتراكات المدرسين:
    1. تنبيه المدرسين قبل 3 أيام من الانتهاء.
    2. تسجيل انتهاء الصلاحية للمدرسين المنتهية اشتراكاتهم.
    """
    today = timezone.now().date()
    three_days_later = today + timedelta(days=3)

    # 1. المدرسون الذين ينتهي اشتراكهم خلال 3 أيام بالضبط
    expiring_soon = Teacher.objects.filter(subscription_expiry=three_days_later)
    for teacher in expiring_soon:
        Notification.objects.create(
            user=teacher.user,
            title="تنبيه: اقترب موعد انتهاء اشتراكك",
            message=f"مرحباً {teacher.user.first_name}، ينتهي اشتراكك خلال 3 أيام. يرجى التجديد لضمان استمرار الخدمة.",
            notification_type='expiry',
            link="/profile/subscription/"
        )

    # 2. المدرسون الذين انتهى اشتراكهم فعلياً (subscription_expiry < today)
    # يمكننا إضافة منطق هنا مثل إرسال بريد إلكتروني أخير أو تغيير حالة معينة
    expired_teachers = Teacher.objects.filter(subscription_expiry__lt=today, is_verified=True)
    for teacher in expired_teachers:
        # ملاحظة: الصلاحيات (Permissions) تمنعهم من النشر بالفعل بناءً على التاريخ
        # ولكن يمكننا إرسال تنبيه نظامي لهم
        Notification.objects.get_or_create(
            user=teacher.user,
            title="انتهى اشتراكك",
            message="لقد انتهى اشتراكك الموثق. يرجى التجديد لاستعادة صلاحيات النشر.",
            notification_type='expiry'
        )
