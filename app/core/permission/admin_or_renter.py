from rest_framework import permissions


class IsAdminOrRenter(permissions.BasePermission):
    """
    Custom permission to only allow access to Admin and Gear Renter users.
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        if hasattr(request.user, 'role') and request.user.role == 'renter':
            return True

        return False
