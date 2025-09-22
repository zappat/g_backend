from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from core.models import User
from .models import Notification
from .serializers import NotificationSerializer, NotificationCreateSerializer, NotificationMarkReadSerializer


class NotificationsByIdView(APIView):
    """
    Get notifications for a user by their id
    URL: /api/notification/notifications/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            # Find user by id
            user = get_object_or_404(User, id=id)
            
            # Get query parameters
            is_read = request.query_params.get('is_read', None)
            notification_type = request.query_params.get('type', None)
            limit = request.query_params.get('limit', None)
            
            # Build queryset
            queryset = Notification.objects.filter(recipient=user)
            
            # Apply filters
            if is_read is not None:
                is_read_bool = is_read.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(is_read=is_read_bool)
            
            if notification_type:
                queryset = queryset.filter(notification_type=notification_type)
            
            # Apply limit
            if limit:
                try:
                    limit_int = int(limit)
                    queryset = queryset[:limit_int]
                except ValueError:
                    pass
            
            # Serialize and return
            serializer = NotificationSerializer(queryset, many=True)
            
            return Response({
                'notifications': serializer.data,
                'total_count': queryset.count(),
                'unread_count': Notification.objects.filter(recipient=user, is_read=False).count()
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this id not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NotificationListCreateView(generics.ListCreateAPIView):
    """
    List all notifications or create a new notification
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter by current user's notifications
        return Notification.objects.filter(recipient=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationCreateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        serializer.save()


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a notification
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only access their own notifications
        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkReadView(APIView):
    """
    Mark one or multiple notifications as read.
    Supports:
    - GET/POST /notifications/mark-read/{pk}/ for single notification
    - POST /notifications/mark-read/ with notification_ids in body for batch update
    """
    permission_classes = [permissions.IsAuthenticated]

    def _mark_single_notification(self, pk, user):
        """Helper method to mark a single notification as read"""
        try:
            notification = Notification.objects.get(
                id=pk,
                recipient=user
            )
            
            if notification.is_read:
                return Response({
                    'message': 'Notification was already marked as read'
                }, status=status.HTTP_200_OK)
            
            notification.is_read = True
            notification.save()
            
            return Response({
                'message': 'Notification marked as read successfully'
            }, status=status.HTTP_200_OK)
            
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found or you do not have permission to access it'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, pk=None):
        if pk is None:
            return Response(
                {'error': 'Notification ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self._mark_single_notification(pk, request.user)


class NotificationMarkAllReadView(APIView):
    """
    Mark all notifications as read for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Get unread notifications
            unread = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            )
            count = unread.count()
            
            if count == 0:
                return Response({
                    'message': 'No unread notifications found',
                    'count': 0
                })
            
            # Update them
            unread.update(is_read=True)
            
            return Response({
                'message': f'Marked {count} notifications as read',
                'count': count
            })
            
        except Exception as e:
            import traceback
            print(f"DEBUG: Error occurred: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
