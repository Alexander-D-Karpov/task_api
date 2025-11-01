import pytest

from task_api.users.api.serializers import (
    UserProfileSerializer,
    UserSearchSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from task_api.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestUserSerializer:
    def test_serialize_user(self, user):
        serializer = UserSerializer(user)
        data = serializer.data

        assert data["email"] == user.email
        assert data["first_name"] == user.first_name
        assert data["last_name"] == user.last_name
        assert "full_name" in data
        assert "tasks_count" in data
        assert "date_joined" in data

    def test_tasks_count(self, user):
        from task_api.tasks.tests.factories import TaskFactory

        TaskFactory.create_batch(3, owner=user)
        serializer = UserSerializer(user)

        assert serializer.data["tasks_count"] == 3

    def test_full_name_with_both_names(self):
        user = UserFactory.create(first_name="John", last_name="Doe")
        serializer = UserSerializer(user)

        assert serializer.data["full_name"] == "John Doe"

    def test_full_name_without_names(self):
        user = UserFactory.create(first_name="", last_name="")
        serializer = UserSerializer(user)

        assert serializer.data["full_name"] == user.email


@pytest.mark.django_db
class TestUserSearchSerializer:
    def test_serialize_user_search(self, user):
        serializer = UserSearchSerializer(user)
        data = serializer.data

        assert data["email"] == user.email
        assert data["first_name"] == user.first_name
        assert data["last_name"] == user.last_name
        assert "full_name" in data

    def test_serializer_fields(self, user):
        serializer = UserSearchSerializer(user)
        data = serializer.data

        assert set(data.keys()) == {"email", "first_name", "last_name", "full_name"}


@pytest.mark.django_db
class TestUserProfileSerializer:
    def test_serialize_user_profile(self, user):
        serializer = UserProfileSerializer(user)
        data = serializer.data

        assert data["email"] == user.email
        assert "tasks_count" in data
        assert "shared_tasks_count" in data

    def test_tasks_and_shared_counts(self, user):
        from task_api.tasks.tests.factories import TaskFactory, TaskShareFactory

        TaskFactory.create_batch(2, owner=user)
        other_user = UserFactory.create()
        task = TaskFactory.create(owner=other_user)
        TaskShareFactory.create(task=task, user=user)

        serializer = UserProfileSerializer(user)

        assert serializer.data["tasks_count"] == 2
        assert serializer.data["shared_tasks_count"] == 1

    def test_read_only_fields(self, user):
        serializer = UserProfileSerializer(user)
        meta = serializer.Meta

        assert "email" in meta.read_only_fields
        assert "date_joined" in meta.read_only_fields


@pytest.mark.django_db
class TestUserUpdateSerializer:
    def test_update_user(self, user):
        data = {
            "first_name": "Updated",
            "last_name": "Name",
        }
        serializer = UserUpdateSerializer(user, data=data, partial=True)

        assert serializer.is_valid()
        updated_user = serializer.save()

        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"

    def test_serializer_only_has_allowed_fields(self):
        serializer = UserUpdateSerializer()
        fields = serializer.Meta.fields

        assert set(fields) == {"first_name", "last_name"}
