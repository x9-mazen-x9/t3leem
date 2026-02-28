from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Load configuration from Django settings, using CELERY_ namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in installed apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

from celery.schedules import crontab

app.conf.beat_schedule = {
    'update-trending-posts-every-5-minutes': {
        'task': 'apps.social.tasks.calculate_trending_posts',
        'schedule': crontab(minute='*/5'),
    },
}

