import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("task_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send-deadline-reminders": {
        "task": "task_api.tasks.tasks.send_deadline_reminders",
        "schedule": crontab(hour=9, minute=0),
    },
}
