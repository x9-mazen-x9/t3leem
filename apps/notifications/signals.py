from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.social.models import Post, Comment, PostLike
from apps.notifications.models import Notification


# ─── منشور جديد → إشعار للطلاب المشتركين ───────────────────────────────────

@receiver(post_save, sender=Post)
def notify_students_new_post(sender, instance, created, **kwargs):
    if not created:
        return

    teacher = instance.author_teacher
    if not teacher:
        return

    try:
        from apps.notifications.tasks import fanout_post_created_notifications
        fanout_post_created_notifications.delay(instance.id)
    except Exception:
        pass


# ─── تعليق جديد → إشعار للمدرس ─────────────────────────────────────────────

@receiver(post_save, sender=Comment)
def notify_comment_reply(sender, instance, created, **kwargs):
    if not created:
        return

    post = instance.post
    owner_user = None
    if post.author_teacher:
        owner_user = post.author_teacher.user
    elif post.author_student:
        owner_user = post.author_student.user
    if not owner_user:
        return

    instance_user = None
    if instance.student:
        instance_user = instance.student.user
    elif instance.teacher_author:
        instance_user = instance.teacher_author.user

    if instance_user and owner_user and instance_user == owner_user:
        return

    Notification.objects.create(
        user=owner_user,
        title="تعليق جديد على منشورك",
        message=(
            f"قام {instance_user.get_full_name() if instance_user else 'مستخدم'} "
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
    owner_user = None
    if post.author_teacher:
        owner_user = post.author_teacher.user
    elif post.author_student:
        owner_user = post.author_student.user
    if not owner_user:
        return

    # لا تُبلّغ المدرس لو أعجب بمنشوره بنفسه
    if instance.user == owner_user:
        return

    Notification.objects.create(
        user=owner_user,
        title="إعجاب جديد بمنشورك",
        message=(
            f"أعجب {instance.user.get_full_name()} "
            f"بمنشور \"{post.title}\""
        ),
        notification_type='like',
        link=f"/posts/{post.id}/",
    )
