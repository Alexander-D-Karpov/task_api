from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from task_api.users.models import User

from .serializers import (
    UserProfileSerializer,
    UserSearchSerializer,
    UserUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Пользователи"],
        summary="Поиск пользователей",
        description="Поиск пользователей по email, имени и фамилии",
        parameters=[
            OpenApiParameter(
                "search",
                OpenApiTypes.STR,
                description="Поиск по email, имени или фамилии",
            ),
            OpenApiParameter(
                "ordering",
                OpenApiTypes.STR,
                description="Сортировка (доступные поля: email, first_name, last_name, date_joined)",
            ),
        ],
    ),
)
class UserSearchView(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["email", "first_name", "last_name", "date_joined"]
    ordering = ["email"]

    def get_queryset(self):
        return (
            User.objects.filter(is_active=True)
            .exclude(id=self.request.user.id)
            .only("email", "first_name", "last_name")
        )


@extend_schema_view(
    retrieve=extend_schema(
        tags=["Пользователи"],
        summary="Профиль пользователя",
        description="Получение информации о профиле пользователя",
    ),
    update=extend_schema(
        tags=["Пользователи"],
        summary="Обновление профиля",
        description="Полное обновление профиля текущего пользователя",
    ),
    partial_update=extend_schema(
        tags=["Пользователи"],
        summary="Частичное обновление профиля",
        description="Частичное обновление профиля текущего пользователя",
    ),
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserProfileSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id).prefetch_related("owned_tasks", "shared_tasks")
