import pytest

from task_api.users.models import User


@pytest.mark.django_db
class TestUserModel:
    def test_user_create(self, user: User):
        assert user.email
        assert user.is_active

    def test_user_password(self, user: User):
        password = "TestPassword123!"
        user.set_password(password)
        user.save()
        assert user.check_password(password)

    def test_user_str(self, user: User):
        assert str(user) == user.email

    def test_user_full_name_with_both_names(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="test123",
            first_name="John",
            last_name="Doe",
        )
        assert user.full_name == "John Doe"

    def test_user_full_name_without_names(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="test123",
        )
        assert user.full_name == "test@example.com"

    def test_user_full_name_with_only_first_name(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="test123",
            first_name="John",
        )
        assert user.full_name == "test@example.com"

    def test_get_short_name_with_first_name(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="test123",
            first_name="John",
        )
        assert user.get_short_name() == "John"

    def test_get_short_name_without_first_name(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="test123",
        )
        assert user.get_short_name() == "test@example.com"

    def test_user_email_unique(self):
        User.objects.create_user(email="test@example.com", password="test123")
        with pytest.raises(Exception):
            User.objects.create_user(email="test@example.com", password="test456")

    def test_user_username_field_is_email(self):
        assert User.USERNAME_FIELD == "email"

    def test_user_required_fields_empty(self):
        assert User.REQUIRED_FIELDS == []
