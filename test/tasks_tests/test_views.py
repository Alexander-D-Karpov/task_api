import pytest
from django.urls import reverse
from rest_framework import status

from task_api.tasks.models import Task, TaskShare
from task_api.tasks.tests.factories import TaskFactory, TaskShareFactory
from task_api.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestTaskListCreateView:
    def test_list_tasks_authenticated(self, api_client, user):
        api_client.force_authenticate(user=user)
        TaskFactory.create_batch(3, owner=user)
        TaskFactory.create_batch(2)

        response = api_client.get(reverse("api:tasks:task-list"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_list_tasks_unauthenticated(self, api_client):
        response = api_client.get(reverse("api:tasks:task-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_task(self, api_client, user):
        api_client.force_authenticate(user=user)
        data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": "new",
            "priority": "high",
        }

        response = api_client.post(reverse("api:tasks:task-list"), data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.filter(owner=user, title="Test Task").exists()

    def test_filter_by_status(self, api_client, user):
        api_client.force_authenticate(user=user)
        TaskFactory.create(owner=user, status=Task.Status.NEW)
        TaskFactory.create(owner=user, status=Task.Status.DONE)

        response = api_client.get(reverse("api:tasks:task-list"), {"status": "new"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_search_tasks(self, api_client, user):
        api_client.force_authenticate(user=user)
        TaskFactory.create(owner=user, title="Important Meeting")
        TaskFactory.create(owner=user, title="Random Task")

        response = api_client.get(reverse("api:tasks:task-list"), {"search": "Meeting"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestTaskDetailView:
    def test_retrieve_task(self, api_client, user):
        api_client.force_authenticate(user=user)
        task = TaskFactory.create(owner=user)

        response = api_client.get(reverse("api:tasks:task-detail", kwargs={"pk": task.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == task.title

    def test_update_task(self, api_client, user):
        api_client.force_authenticate(user=user)
        task = TaskFactory.create(owner=user)
        data = {"title": "Updated Title", "status": "done"}

        response = api_client.patch(reverse("api:tasks:task-detail", kwargs={"pk": task.pk}), data=data)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == "Updated Title"
        assert task.status == "done"

    def test_delete_task(self, api_client, user):
        api_client.force_authenticate(user=user)
        task = TaskFactory.create(owner=user)

        response = api_client.delete(reverse("api:tasks:task-detail", kwargs={"pk": task.pk}))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_cannot_update_others_task(self, api_client):
        user1 = UserFactory.create()
        user2 = UserFactory.create()
        task = TaskFactory.create(owner=user1)

        api_client.force_authenticate(user=user2)
        response = api_client.patch(
            reverse("api:tasks:task-detail", kwargs={"pk": task.pk}),
            data={"title": "Hacked"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestShareTaskView:
    def test_share_task(self, api_client, user):
        api_client.force_authenticate(user=user)
        task = TaskFactory.create(owner=user)
        other_user = UserFactory.create()

        data = {"email": other_user.email, "permission": "view"}
        response = api_client.post(reverse("api:tasks:task-share", kwargs={"pk": task.pk}), data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert TaskShare.objects.filter(task=task, user=other_user).exists()

    def test_cannot_share_with_owner(self, api_client, user):
        api_client.force_authenticate(user=user)
        task = TaskFactory.create(owner=user)

        data = {"email": user.email, "permission": "view"}
        response = api_client.post(reverse("api:tasks:task-share", kwargs={"pk": task.pk}), data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_shared_user_can_view(self, api_client):
        owner = UserFactory.create()
        viewer = UserFactory.create()
        task = TaskFactory.create(owner=owner)
        TaskShareFactory.create(task=task, user=viewer, permission="view")

        api_client.force_authenticate(user=viewer)
        response = api_client.get(reverse("api:tasks:task-detail", kwargs={"pk": task.pk}))

        assert response.status_code == status.HTTP_200_OK

    def test_shared_user_with_edit_can_update(self, api_client):
        owner = UserFactory.create()
        editor = UserFactory.create()
        task = TaskFactory.create(owner=owner)
        TaskShareFactory.create(task=task, user=editor, permission="edit")

        api_client.force_authenticate(user=editor)
        response = api_client.patch(
            reverse("api:tasks:task-detail", kwargs={"pk": task.pk}),
            data={"title": "Updated by editor"},
        )

        assert response.status_code == status.HTTP_200_OK

    def test_shared_user_with_view_cannot_update(self, api_client):
        owner = UserFactory.create()
        viewer = UserFactory.create()
        task = TaskFactory.create(owner=owner)
        TaskShareFactory.create(task=task, user=viewer, permission="view")

        api_client.force_authenticate(user=viewer)
        response = api_client.patch(
            reverse("api:tasks:task-detail", kwargs={"pk": task.pk}),
            data={"title": "Hacked"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
