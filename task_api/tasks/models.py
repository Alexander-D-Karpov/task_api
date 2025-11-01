from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Завершена"

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    priority = models.CharField("Приоритет", max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    deadline = models.DateTimeField("Крайний срок", null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_tasks",
        verbose_name="Владелец",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["owner", "priority"]),
            models.Index(fields=["deadline"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.deadline and self.status != self.Status.DONE:
            return timezone.now() > self.deadline
        return False


class TaskShare(models.Model):
    class Permission(models.TextChoices):
        VIEW = "view", "Просмотр"
        EDIT = "edit", "Редактирование"

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="shares", verbose_name="Задача")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shared_tasks",
        verbose_name="Пользователь",
    )
    permission = models.CharField(
        "Уровень доступа",
        max_length=10,
        choices=Permission.choices,
        default=Permission.VIEW,
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Общий доступ к задаче"
        verbose_name_plural = "Общий доступ к задачам"
        unique_together = ["task", "user"]
        indexes = [
            models.Index(fields=["user", "task"]),
        ]

    def __str__(self):
        return f"{self.task.title} - {self.user.email} ({self.get_permission_display()})"
