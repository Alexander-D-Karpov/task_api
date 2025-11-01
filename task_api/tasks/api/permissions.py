from rest_framework import permissions


class IsOwnerOrSharedWithEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user or obj.shares.filter(user=request.user).exists()

        if obj.owner == request.user:
            return True

        return obj.shares.filter(user=request.user, permission="edit").exists()


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
