from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import Review
from .serializers import ReviewSerializer
from django.db import models
from core.models import User
import logging

logger = logging.getLogger(__name__)

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

    def create(self, request, *args, **kwargs):
        logger.info(f"Review creation request data: {request.data}")
        logger.info(f"Request user: {request.user}")
        logger.info(f"User role: {getattr(request.user, 'role', 'No role')}")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            logger.error(f"Review validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(renter=self.request.user)

    @action(detail=False, methods=['get'], url_path='get-by-user/(?P<user_id>[^/.]+)')
    def get_by_user(self, request, user_id=None):
        """
        Get reviews for a specific user by user ID.
        URL: /api/review/reviews/get-by-user/{user_id}/
        """
        try:
            # Get the user
            user = User.objects.get(id=user_id)
            
            # Get reviews where the user is either the renter or merchant
            reviews = Review.objects.filter(
                models.Q(merchant=user)
            ).order_by('-created_at')
            
            # Serialize the reviews
            serializer = self.get_serializer(reviews, many=True)
            
            return Response({
                'user_id': user_id,
                'user_email': user.email,
                'reviews': serializer.data,
                'count': reviews.count()
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'error': f'User with ID {user_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting reviews by user: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 