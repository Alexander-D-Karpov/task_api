from django.contrib import admin

from .models import Task, TaskShare


class TaskShareInline(admin.TabularInline):
    model = TaskShare
    extra = 1
    autocomplete_fields = ["user"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "status", "priority", "deadline", "created_at", "is_overdue"]
    list_filter = ["status", "priority", "created_at", "deadline"]
    search_fields = ["title", "description", "owner__email"]
    autocomplete_fields = ["owner"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at"]
    inlines = [TaskShareInline]
    fieldsets = (
        (None, {"fields": ("title", "description")}),
        (
            "Статус и приоритет",
            {"fields": ("status", "priority", "deadline")},
        ),
        ("Владелец", {"fields": ("owner",)}),
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )

    def is_overdue(self, obj):
        return obj.is_overdue

    is_overdue.boolean = True
    is_overdue.short_description = "Просрочена"


@admin.register(TaskShare)
class TaskShareAdmin(admin.ModelAdmin):
    list_display = ["task", "user", "permission", "created_at"]
    list_filter = ["permission", "created_at"]
    search_fields = ["task__title", "user__email"]
    autocomplete_fields = ["task", "user"]
    date_hierarchy = "created_at"
