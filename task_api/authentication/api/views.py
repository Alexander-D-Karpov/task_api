from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, UserSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Аутентификация"],
        summary="Регистрация пользователя",
        description="Создание нового аккаунта пользователя",
    )
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "Пользователь успешно зарегистрирован",
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Аутентификация"],
    summary="Получение JWT токена",
    description="Аутентификация пользователя по email и паролю",
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=["Аутентификация"],
    summary="Обновление JWT токена",
    description="Получение нового access токена используя refresh токен",
)
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
