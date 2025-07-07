from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer
from django.db import models

class IsRenterOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.is_authenticated and request.user.role == 'renter'
        return True

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsRenterOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        # Show reviews given or received by the user
        return Review.objects.filter(models.Q(renter=user) | models.Q(merchant=user)).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(renter=self.request.user) 