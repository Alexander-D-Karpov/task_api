from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from task_api.tasks.models import Task, TaskShare

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    shared_with = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "deadline",
            "owner",
            "owner_email",
            "is_overdue",
            "shared_with",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    @extend_schema_field(serializers.IntegerField)
    def get_shared_with(self, obj) -> int:
        return obj.shares.count()

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class TaskShareSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = TaskShare
        fields = ["id", "task", "task_title", "user", "user_email", "permission", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        task = attrs.get("task")
        user = attrs.get("user")

        if task.owner == user:
            raise serializers.ValidationError("Нельзя поделиться задачей с владельцем")

        request_user = self.context["request"].user
        if task.owner != request_user:
            raise serializers.ValidationError("Вы можете делиться только своими задачами")

        return attrs


class ShareTaskSerializer(serializers.Serializer):
    email = serializers.EmailField()
    permission = serializers.ChoiceField(choices=TaskShare.Permission.choices)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден")

        task = self.context.get("task")
        if task and task.owner == user:
            raise serializers.ValidationError("Нельзя поделиться задачей с владельцем")

        return value
