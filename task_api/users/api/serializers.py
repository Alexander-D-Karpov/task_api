from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "full_name",
            "date_joined",
            "tasks_count",
        ]
        read_only_fields = ["date_joined", "is_active"]

    @extend_schema_field(serializers.CharField)
    def get_full_name(self, obj) -> str:
        return obj.full_name

    @extend_schema_field(serializers.IntegerField)
    def get_tasks_count(self, obj) -> int:
        return obj.owned_tasks.count()


class UserSearchSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "full_name",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    tasks_count = serializers.SerializerMethodField()
    shared_tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "full_name",
            "date_joined",
            "tasks_count",
            "shared_tasks_count",
        ]
        read_only_fields = ["email", "date_joined"]

    @extend_schema_field(serializers.IntegerField)
    def get_tasks_count(self, obj) -> int:
        return obj.owned_tasks.count()

    @extend_schema_field(serializers.IntegerField)
    def get_shared_tasks_count(self, obj) -> int:
        return obj.shared_tasks.count()


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
