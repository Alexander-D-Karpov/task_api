import pytest
from django.urls import reverse
from rest_framework import status

from task_api.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestUserSearchView:
    def test_search_users_authenticated(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create_batch(3)

        response = api_client.get(reverse("api:users:user-search"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 3

    def test_search_users_unauthenticated(self, api_client):
        UserFactory.create_batch(3)
        response = api_client.get(reverse("api:users:user-search"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_users_by_email(self, api_client, user):
        api_client.force_authenticate(user=user)
        target_user = UserFactory.create(email="specific@example.com")
        UserFactory.create_batch(2)

        response = api_client.get(reverse("api:users:user-search"), {"search": "specific"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["email"] == target_user.email

    def test_search_users_by_first_name(self, api_client, user):
        api_client.force_authenticate(user=user)
        target_user = UserFactory.create(first_name="Alexander")
        UserFactory.create_batch(2)

        response = api_client.get(reverse("api:users:user-search"), {"search": "Alexander"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["first_name"] == target_user.first_name

    def test_search_users_by_last_name(self, api_client, user):
        api_client.force_authenticate(user=user)
        target_user = UserFactory.create(last_name="Smith")
        UserFactory.create_batch(2)

        response = api_client.get(reverse("api:users:user-search"), {"search": "Smith"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["last_name"] == target_user.last_name

    def test_search_excludes_current_user(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create_batch(5)

        response = api_client.get(reverse("api:users:user-search"))

        assert response.status_code == status.HTTP_200_OK
        user_emails = [result["email"] for result in response.data["results"]]
        assert user.email not in user_emails

    def test_search_excludes_inactive_users(self, api_client, user):
        api_client.force_authenticate(user=user)
        inactive_user = UserFactory.create(is_active=False)
        active_user = UserFactory.create(is_active=True)

        response = api_client.get(reverse("api:users:user-search"))

        assert response.status_code == status.HTTP_200_OK
        user_emails = [result["email"] for result in response.data["results"]]
        assert inactive_user.email not in user_emails
        assert active_user.email in user_emails

    def test_search_ordering_by_email(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create(email="charlie@example.com")
        UserFactory.create(email="alice@example.com")
        UserFactory.create(email="bob@example.com")

        response = api_client.get(reverse("api:users:user-search"), {"ordering": "email"})

        assert response.status_code == status.HTTP_200_OK
        emails = [result["email"] for result in response.data["results"]]
        assert emails == sorted(emails)

    def test_search_ordering_by_first_name(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create(first_name="Charlie")
        UserFactory.create(first_name="Alice")
        UserFactory.create(first_name="Bob")

        response = api_client.get(reverse("api:users:user-search"), {"ordering": "first_name"})

        assert response.status_code == status.HTTP_200_OK
        first_names = [result["first_name"] for result in response.data["results"]]
        assert first_names == sorted(first_names)

    def test_search_response_structure(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create()

        response = api_client.get(reverse("api:users:user-search"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) > 0
        result = response.data["results"][0]
        assert "email" in result
        assert "first_name" in result
        assert "last_name" in result
        assert "full_name" in result

    def test_search_pagination(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create_batch(25)

        response = api_client.get(reverse("api:users:user-search"))

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    def test_search_empty_query(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create_batch(3)

        response = api_client.get(reverse("api:users:user-search"), {"search": ""})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_search_no_results(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create_batch(3)

        response = api_client.get(reverse("api:users:user-search"), {"search": "nonexistent"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0


@pytest.mark.django_db
class TestUserProfileView:
    def test_get_profile(self, api_client, user):
        api_client.force_authenticate(user=user)

        response = api_client.get(reverse("api:users:user-profile"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert "full_name" in response.data
        assert "tasks_count" in response.data
        assert "shared_tasks_count" in response.data
        assert "date_joined" in response.data

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get(reverse("api:users:user-profile"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_first_name(self, api_client, user):
        api_client.force_authenticate(user=user)
        data = {"first_name": "Updated"}

        response = api_client.patch(reverse("api:users:user-profile"), data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "Updated"

    def test_update_profile_last_name(self, api_client, user):
        api_client.force_authenticate(user=user)
        data = {"last_name": "UpdatedLast"}

        response = api_client.patch(reverse("api:users:user-profile"), data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.last_name == "UpdatedLast"

    def test_update_profile_both_names(self, api_client, user):
        api_client.force_authenticate(user=user)
        data = {
            "first_name": "John",
            "last_name": "Doe",
        }

        response = api_client.patch(reverse("api:users:user-profile"), data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_full_update_profile(self, api_client, user):
        api_client.force_authenticate(user=user)
        data = {
            "first_name": "John",
            "last_name": "Doe",
        }

        response = api_client.put(reverse("api:users:user-profile"), data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_cannot_update_email_through_profile(self, api_client, user):
        api_client.force_authenticate(user=user)
        original_email = user.email
        data = {
            "email": "newemail@example.com",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = api_client.patch(reverse("api:users:user-profile"), data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == original_email

    def test_cannot_update_is_active_through_profile(self, api_client, user):
        api_client.force_authenticate(user=user)
        data = {
            "is_active": False,
            "first_name": "John",
        }

        response = api_client.patch(reverse("api:users:user-profile"), data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_active is True

    def test_profile_response_structure(self, api_client, user):
        api_client.force_authenticate(user=user)

        response = api_client.get(reverse("api:users:user-profile"))

        assert response.status_code == status.HTTP_200_OK
        assert "email" in response.data
        assert "first_name" in response.data
        assert "last_name" in response.data
        assert "full_name" in response.data
        assert "date_joined" in response.data
        assert "tasks_count" in response.data
        assert "shared_tasks_count" in response.data

    def test_update_profile_empty_names(self, api_client, user):
        api_client.force_authenticate(user=user)
        user.first_name = "John"
        user.last_name = "Doe"
        user.save()

        data = {
            "first_name": "",
            "last_name": "",
        }

        response = api_client.patch(reverse("api:users:user-profile"), data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == ""
        assert user.last_name == ""

    def test_profile_tasks_count_with_tasks(self, api_client, user):
        from task_api.tasks.tests.factories import TaskFactory

        api_client.force_authenticate(user=user)
        TaskFactory.create_batch(3, owner=user)

        response = api_client.get(reverse("api:users:user-profile"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["tasks_count"] == 3

    def test_profile_shared_tasks_count_with_shared_tasks(self, api_client, user):
        from task_api.tasks.tests.factories import TaskFactory, TaskShareFactory

        api_client.force_authenticate(user=user)
        other_user = UserFactory.create()
        tasks = TaskFactory.create_batch(2, owner=other_user)
        for task in tasks:
            TaskShareFactory.create(task=task, user=user)

        response = api_client.get(reverse("api:users:user-profile"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["shared_tasks_count"] == 2


@pytest.mark.django_db
class TestUserSearchViewEdgeCases:
    def test_search_case_insensitive(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create(email="TEST@example.com")

        response = api_client.get(reverse("api:users:user-search"), {"search": "test"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_search_partial_match(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create(email="testuser@example.com")
        UserFactory.create(email="anothertest@example.com")

        response = api_client.get(reverse("api:users:user-search"), {"search": "test"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_ordering_descending(self, api_client, user):
        api_client.force_authenticate(user=user)
        UserFactory.create(email="alice@example.com")
        UserFactory.create(email="bob@example.com")
        UserFactory.create(email="charlie@example.com")

        response = api_client.get(reverse("api:users:user-search"), {"ordering": "-email"})

        assert response.status_code == status.HTTP_200_OK
        emails = [result["email"] for result in response.data["results"]]
        assert emails == sorted(emails, reverse=True)
