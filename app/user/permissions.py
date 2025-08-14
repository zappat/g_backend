from rest_framework.permissions import BasePermission
from django.utils import timezone

class IsProvider(BasePermission):
    """Permission to check if the user's role is a gear provider"""
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == "gear_provider":
            return True
        return False


class IsProMerchant(BasePermission):
    """Allows access only to authenticated pro merchants."""
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or getattr(user, 'role', None) != 'merchant':
            return False
        profile = getattr(user, 'merchantprofile', None)
        if profile is None:
            return False
        if not profile.is_pro:
            return False
        if profile.pro_expires_at is None:
            return True
        return profile.pro_expires_at > timezone.now()