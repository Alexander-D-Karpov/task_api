from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from task_api.tasks.api.filters import TaskFilter
from task_api.tasks.api.permissions import IsOwner, IsOwnerOrSharedWithEdit
from task_api.tasks.api.serializers import ShareTaskSerializer, TaskSerializer, TaskShareSerializer
from task_api.tasks.models import Task, TaskShare

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        tags=["Задачи"],
        summary="Список задач",
        description="Получение списка задач пользователя (своих и расшаренных)",
        parameters=[
            OpenApiParameter(
                "status", OpenApiTypes.STR, description="Фильтр по статусу (можно указать несколько через запятую)"
            ),
            OpenApiParameter(
                "priority", OpenApiTypes.STR, description="Фильтр по приоритету (можно указать несколько через запятую)"
            ),
            OpenApiParameter("deadline_after", OpenApiTypes.DATETIME, description="Дедлайн после указанной даты"),
            OpenApiParameter("deadline_before", OpenApiTypes.DATETIME, description="Дедлайн до указанной даты"),
            OpenApiParameter("is_overdue", OpenApiTypes.BOOL, description="Просроченные задачи"),
            OpenApiParameter("search", OpenApiTypes.STR, description="Поиск по названию и описанию"),
            OpenApiParameter(
                "ordering",
                OpenApiTypes.STR,
                description="Сортировка (доступные поля: created_at, deadline, priority, status)",
            ),
        ],
    ),
    create=extend_schema(
        tags=["Задачи"],
        summary="Создание задачи",
        description="Создание новой задачи",
    ),
)
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "deadline", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()

        user = self.request.user
        return (
            Task.objects.filter(Q(owner=user) | Q(shares__user=user))
            .select_related("owner")
            .prefetch_related(Prefetch("shares", queryset=TaskShare.objects.select_related("user")))
            .distinct()
        )


@extend_schema_view(
    retrieve=extend_schema(
        tags=["Задачи"],
        summary="Детали задачи",
        description="Получение информации о конкретной задаче",
    ),
    update=extend_schema(
        tags=["Задачи"],
        summary="Полное обновление задачи",
        description="Полное обновление всех полей задачи",
    ),
    partial_update=extend_schema(
        tags=["Задачи"],
        summary="Частичное обновление задачи",
        description="Обновление отдельных полей задачи",
    ),
    destroy=extend_schema(
        tags=["Задачи"],
        summary="Удаление задачи",
        description="Удаление задачи (только для владельца)",
    ),
)
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSharedWithEdit]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()

        user = self.request.user
        return (
            Task.objects.filter(Q(owner=user) | Q(shares__user=user))
            .select_related("owner")
            .prefetch_related(Prefetch("shares", queryset=TaskShare.objects.select_related("user")))
            .distinct()
        )


@extend_schema_view(
    post=extend_schema(
        tags=["Расшаривание задач"],
        summary="Поделиться задачей",
        description="Предоставить доступ к задаче другому пользователю",
    ),
)
class ShareTaskView(generics.GenericAPIView):
    serializer_class = ShareTaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()

        return Task.objects.filter(owner=self.request.user)

    def post(self, request, pk):
        task = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"task": task})
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])
        permission = serializer.validated_data["permission"]

        share, created = TaskShare.objects.update_or_create(
            task=task,
            user=user,
            defaults={"permission": permission},
        )

        return Response(
            {
                "message": "Доступ успешно предоставлен" if created else "Доступ обновлен",
                "share": TaskShareSerializer(share).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(
        tags=["Расшаривание задач"],
        summary="Список общих доступов",
        description="Получение списка пользователей, с которыми задача поделена",
    ),
)
class TaskShareListView(generics.ListAPIView):
    serializer_class = TaskShareSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TaskShare.objects.none()

        task_id = self.kwargs.get("pk")
        return TaskShare.objects.filter(task_id=task_id, task__owner=self.request.user).select_related("user", "task")


@extend_schema_view(
    destroy=extend_schema(
        tags=["Расшаривание задач"],
        summary="Удалить общий доступ",
        description="Отозвать доступ пользователя к задаче",
    ),
)
class TaskShareDeleteView(generics.DestroyAPIView):
    serializer_class = TaskShareSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TaskShare.objects.none()

        return TaskShare.objects.filter(task__owner=self.request.user)
