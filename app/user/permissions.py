from rest_framework.permissions import BasePermission

class IsProvider(BasePermission):
    """Permission to check if the user's role is a gear provider"""
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == "gear_provider":
            return True
        return False