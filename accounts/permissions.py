from rest_framework.permissions import BasePermission


class IsStaffOrAdmin(BasePermission):
    """
    Allows access only to users with staff or admin role.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["staff", "admin"]
        )

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )