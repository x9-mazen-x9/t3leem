from celery import shared_task
from django.db import transaction
from django.apps import apps
from .bunny import create_bunny_video


@shared_task
def create_bunny_video_task(lesson_id, title):
    Lesson = apps.get_model('lessons', 'Lesson')
    try:
        video_id = create_bunny_video(title)
    except Exception:
        return
    with transaction.atomic():
        lesson = Lesson.objects.select_for_update().filter(id=lesson_id).first()
        if lesson and not lesson.bunny_video_id:
            lesson.bunny_video_id = video_id
            lesson.save(update_fields=["bunny_video_id"])
