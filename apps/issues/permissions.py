
from rest_framework import permissions


class IsRegisteredUser(permissions.BasePermission):
    message = "Only registered users can report issues."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.role_name == "Registered User"
        )
