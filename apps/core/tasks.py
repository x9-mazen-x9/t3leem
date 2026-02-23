from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_notification(notification_type: str, payload: dict | None = None) -> None:
    """
    مهمة عامة لإرسال الإشعارات (بريد، Push، Webhook...).
    في هذه المرحلة يتم فقط تسجيل الحدث في اللوج كـ Proof of Concept.

    مثال لاستخدامها:
        send_notification.delay("teacher_verified", {"teacher_id": 1})
        send_notification.delay("student_enrolled", {"student_id": 5, "teacher_id": 3})
    """
    payload = payload or {}
    logger.info("Notification event: %s | payload=%s", notification_type, payload)

