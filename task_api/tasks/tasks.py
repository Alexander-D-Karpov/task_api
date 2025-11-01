from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


@shared_task
def send_deadline_reminders():
    from .models import Task

    tomorrow = timezone.now() + timedelta(days=1)
    tasks = Task.objects.filter(
        deadline__date=tomorrow.date(),
        status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS],
    ).select_related("owner")

    for task in tasks:
        # здесь просто формируем, но лучше использовать шаблоны писем
        send_mail(
            subject=f"Напоминание: задача '{task.title}' должна быть выполнена завтра",
            message=f"""
Здравствуйте, {task.owner.email}!

Напоминаем, что завтра ({tomorrow.strftime("%d.%m.%Y")}) истекает срок выполнения задачи:

Название: {task.title}
Описание: {task.description}
Приоритет: {task.get_priority_display()}
Статус: {task.get_status_display()}

Не забудьте выполнить задачу вовремя!
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.owner.email],
            fail_silently=True,
        )

    return f"Отправлено {tasks.count()} напоминаний"
