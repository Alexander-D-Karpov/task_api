from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
        "full_name_display",
        "is_staff",
        "is_active",
        "date_joined",
        "tasks_count",
    ]
    list_filter = ["is_staff", "is_superuser", "is_active", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]
    readonly_fields = ["date_joined", "last_login"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональная информация",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    def full_name_display(self, obj):
        return obj.full_name

    full_name_display.short_description = "Полное имя"

    def tasks_count(self, obj):
        return obj.owned_tasks.count()

    tasks_count.short_description = "Количество задач"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("owned_tasks")
