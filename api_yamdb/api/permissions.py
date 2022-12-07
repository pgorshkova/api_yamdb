from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permissions - Администратор или только для чтения"""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorOrModeRatOrOrAdminOrReadOnly(
    permissions.IsAuthenticatedOrReadOnly
):
    """Permissions - Администратор, модератор, автор или только для чтения"""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdmin(permissions.BasePermission):
    """Permissions - только Администратор"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )
