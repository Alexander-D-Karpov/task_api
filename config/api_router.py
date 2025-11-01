from django.urls import include, path

app_name = "api"
urlpatterns = [
    path("auth/", include("task_api.authentication.api.urls", namespace="authentication")),
    path("tasks/", include("task_api.tasks.api.urls", namespace="tasks")),
    path("users/", include("task_api.users.api.urls", namespace="users")),
]
