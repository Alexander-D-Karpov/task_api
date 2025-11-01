from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from task_api.tasks.models import Task, TaskShare
from task_api.users.tests.factories import UserFactory


class TaskFactory(DjangoModelFactory):
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("text")
    status = factory.Iterator([choice[0] for choice in Task.Status.choices])
    priority = factory.Iterator([choice[0] for choice in Task.Priority.choices])
    deadline = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = Task


class TaskShareFactory(DjangoModelFactory):
    task = factory.SubFactory(TaskFactory)
    user = factory.SubFactory(UserFactory)
    permission = factory.Iterator([choice[0] for choice in TaskShare.Permission.choices])

    class Meta:
        model = TaskShare
