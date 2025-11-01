from django.utils import timezone
from django_filters import rest_framework as filters

from task_api.tasks.models import Task


class TaskFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(choices=Task.Status.choices)
    priority = filters.MultipleChoiceFilter(choices=Task.Priority.choices)
    deadline_after = filters.DateTimeFilter(field_name="deadline", lookup_expr="gte")
    deadline_before = filters.DateTimeFilter(field_name="deadline", lookup_expr="lte")
    is_overdue = filters.BooleanFilter(method="filter_overdue")

    class Meta:
        model = Task
        fields = ["status", "priority", "deadline_after", "deadline_before"]

    def filter_overdue(self, queryset, name, value):
        if value:
            return queryset.filter(deadline__lt=timezone.now()).exclude(status=Task.Status.DONE)
        return queryset.exclude(deadline__lt=timezone.now(), status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS])
