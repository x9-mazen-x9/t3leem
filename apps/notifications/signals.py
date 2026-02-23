from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.social.models import Post, Comment, PostLike
from apps.notifications.models import Notification
from apps.students.models import Student, Enrollment


# ─── منشور جديد → إشعار للطلاب المشتركين ───────────────────────────────────

@receiver(post_save, sender=Post)
def notify_students_new_post(sender, instance, created, **kwargs):
    if not created or not instance.created_by:
        return

    teacher = instance.created_by

    from django.utils import timezone
    active_enrollments = Enrollment.objects.filter(
        course__teacher=teacher,
        is_active=True,
        is_pending=False,
        expiry_date__gte=timezone.now().date(),
    ).select_related('student__user')

    student_users = [e.student.user for e in active_enrollments]

    if not student_users:
        return

    notifications = [
        Notification(
            user=user,
            title=f"منشور جديد من {teacher.user.get_full_name()}",
            message=f"قام المدرس {teacher.user.get_full_name()} بنشر: {instance.title}",
            notification_type='post',
            link=f"/posts/{instance.id}/",
        )
        for user in student_users
    ]
    Notification.objects.bulk_create(notifications)


# ─── تعليق جديد → إشعار للمدرس ─────────────────────────────────────────────

@receiver(post_save, sender=Comment)
def notify_comment_reply(sender, instance, created, **kwargs):
    if not created:
        return

    post = instance.post
    if not post.created_by:
        return

    # لا تُبلّغ المدرس لو هو نفسه علّق (حالة نادرة)
    if instance.student.user == post.created_by.user:
        return

    Notification.objects.create(
        user=post.created_by.user,
        title="تعليق جديد على منشورك",
        message=(
            f"قام الطالب {instance.student.user.get_full_name()} "
            f"بالتعليق على \"{post.title}\""
        ),
        notification_type='comment',
        link=f"/posts/{post.id}/",
    )


# ─── إعجاب جديد → إشعار لصاحب المنشور ──────────────────────────────────────

@receiver(post_save, sender=PostLike)
def notify_post_like(sender, instance, created, **kwargs):
    if not created:
        return

    post = instance.post
    if not post.created_by:
        return

    # لا تُبلّغ المدرس لو أعجب بمنشوره بنفسه
    if instance.user == post.created_by.user:
        return

    Notification.objects.create(
        user=post.created_by.user,
        title="إعجاب جديد بمنشورك",
        message=(
            f"أعجب {instance.user.get_full_name()} "
            f"بمنشور \"{post.title}\""
        ),
        notification_type='like',
        link=f"/posts/{post.id}/",
    )
