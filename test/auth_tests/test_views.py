import pytest
from django.urls import reverse
from rest_framework import status

from task_api.users.models import User


@pytest.mark.django_db
class TestRegisterView:
    def test_register_user(self, api_client):
        data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
        }

        response = api_client.post(reverse("api:authentication:register"), data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="test@example.com").exists()

    def test_register_password_mismatch(self, api_client):
        data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "password_confirm": "DifferentPass123!",
        }

        response = api_client.post(reverse("api:authentication:register"), data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, user):
        data = {
            "email": user.email,
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
        }

        response = api_client.post(reverse("api:authentication:register"), data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, api_client, user):
        user.set_password("TestPass123!")
        user.save()

        data = {"email": user.email, "password": "TestPass123!"}
        response = api_client.post(reverse("api:authentication:login"), data=data)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client, user):
        data = {"email": user.email, "password": "WrongPassword"}
        response = api_client.post(reverse("api:authentication:login"), data=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        data = {"email": "nonexistent@example.com", "password": "TestPass123!"}
        response = api_client.post(reverse("api:authentication:login"), data=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
