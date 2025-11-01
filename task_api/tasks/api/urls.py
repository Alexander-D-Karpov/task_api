from django.urls import path

from .views import (
    ShareTaskView,
    TaskDetailView,
    TaskListCreateView,
    TaskShareDeleteView,
    TaskShareListView,
)

app_name = "tasks"

urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("<int:pk>/share/", ShareTaskView.as_view(), name="task-share"),
    path("<int:pk>/shares/", TaskShareListView.as_view(), name="task-shares"),
    path("shares/<int:pk>/", TaskShareDeleteView.as_view(), name="task-share-delete"),
]
