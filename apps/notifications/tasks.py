from __future__ import annotations

import logging
from typing import Iterable, Iterator, List, Optional

from celery import shared_task
from django.db import close_old_connections
from django.utils import timezone

from apps.notifications.models import Notification

logger = logging.getLogger(__name__)


def _chunked(iterable: Iterable[int], chunk_size: int) -> Iterator[List[int]]:
    batch: List[int] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= chunk_size:
            yield batch
            batch = []
    if batch:
        yield batch


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def fanout_post_created_notifications(self, post_id: int) -> dict:
    close_old_connections()
    from apps.social.models import Post
    from apps.teachers.models import Follow

    post = (
        Post.objects.select_related("author_teacher__user")
        .get(pk=post_id)
    )
    teacher = post.author_teacher
    if not teacher:
        return {"status": "skipped", "reason": "no_teacher", "post_id": post_id}

    title = f"منشور جديد من {teacher.user.get_full_name()}"
    message = f"قام المدرس {teacher.user.get_full_name()} بنشر: {post.title}"
    link = f"/posts/{post.id}/"
    dedupe_key = f"post:{post.id}"

    user_ids_qs = (
        Follow.objects.filter(teacher=teacher)
        .values_list("user_id", flat=True)
        .iterator(chunk_size=5000)
    )

    created_total = 0
    processed_total = 0

    for batch_user_ids in _chunked(user_ids_qs, 1000):
        processed_total += len(batch_user_ids)
        notifications = [
            Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type="post",
                link=link,
                dedupe_key=dedupe_key,
            )
            for user_id in batch_user_ids
        ]
        Notification.objects.bulk_create(
            notifications,
            batch_size=1000,
            ignore_conflicts=True,
        )
        created_total += len(notifications)

        if processed_total % 5000 == 0:
            logger.info(
                "fanout_post_created_notifications progress post_id=%s processed=%s",
                post_id,
                processed_total,
            )

    return {
        "status": "done",
        "post_id": post_id,
        "processed": processed_total,
        "attempted_create": created_total,
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def fanout_teacher_broadcast(
    self,
    teacher_id: int,
    title: str,
    message: str,
    broadcast_id: str,
    student_ids: Optional[List[int]] = None,
) -> dict:
    close_old_connections()
    from apps.students.models import Enrollment

    today = timezone.now().date()
    qs = (
        Enrollment.objects.filter(
            course__teacher_id=teacher_id,
            is_active=True,
            is_pending=False,
            expiry_date__gte=today,
        )
        .values_list("student__user_id", flat=True)
        .distinct()
        .iterator(chunk_size=5000)
    )

    if student_ids:
        qs = (
            Enrollment.objects.filter(
                course__teacher_id=teacher_id,
                is_active=True,
                is_pending=False,
                expiry_date__gte=today,
                student_id__in=student_ids,
            )
            .values_list("student__user_id", flat=True)
            .distinct()
            .iterator(chunk_size=5000)
        )

    dedupe_prefix = f"broadcast:teacher:{broadcast_id}"
    created_total = 0
    processed_total = 0

    for batch_user_ids in _chunked(qs, 1000):
        processed_total += len(batch_user_ids)
        notifications = [
            Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type="broadcast",
                dedupe_key=dedupe_prefix,
            )
            for user_id in batch_user_ids
        ]
        Notification.objects.bulk_create(
            notifications,
            batch_size=1000,
            ignore_conflicts=True,
        )
        created_total += len(notifications)

        if processed_total % 5000 == 0:
            logger.info(
                "fanout_teacher_broadcast progress teacher_id=%s processed=%s broadcast_id=%s",
                teacher_id,
                processed_total,
                broadcast_id,
            )

    return {
        "status": "done",
        "teacher_id": teacher_id,
        "broadcast_id": broadcast_id,
        "processed": processed_total,
        "attempted_create": created_total,
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def fanout_platform_broadcast(
    self,
    title: str,
    message: str,
    broadcast_id: str,
    user_ids: Optional[List[int]] = None,
    user_type: Optional[str] = None,
) -> dict:
    close_old_connections()
    from apps.users.models import User

    qs = User.objects.filter(is_active=True).values_list("id", flat=True)
    if user_ids:
        qs = qs.filter(id__in=user_ids)
    if user_type in ("teacher", "student", "admin"):
        qs = qs.filter(user_type=user_type)

    qs = qs.iterator(chunk_size=5000)

    dedupe_prefix = f"broadcast:platform:{broadcast_id}"
    created_total = 0
    processed_total = 0

    for batch_user_ids in _chunked(qs, 1000):
        processed_total += len(batch_user_ids)
        notifications = [
            Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type="broadcast",
                dedupe_key=dedupe_prefix,
            )
            for user_id in batch_user_ids
        ]
        Notification.objects.bulk_create(
            notifications,
            batch_size=1000,
            ignore_conflicts=True,
        )
        created_total += len(notifications)

        if processed_total % 5000 == 0:
            logger.info(
                "fanout_platform_broadcast progress processed=%s broadcast_id=%s",
                processed_total,
                broadcast_id,
            )

    return {
        "status": "done",
        "broadcast_id": broadcast_id,
        "processed": processed_total,
        "attempted_create": created_total,
    }
