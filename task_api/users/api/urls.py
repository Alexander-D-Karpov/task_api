from django.urls import path

from .views import (
    UserProfileView,
    UserSearchView,
)

app_name = "users"

urlpatterns = [
    path("", UserSearchView.as_view(), name="user-search"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
]
