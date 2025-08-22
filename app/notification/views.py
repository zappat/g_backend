from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.models import User
from .models import Notification
from .serializers import NotificationSerializer, NotificationCreateSerializer, NotificationMarkReadSerializer


class NotificationsByEmailView(APIView):
    """
    Get notifications for a user by their email
    URL: /api/notification/notifications/{email}/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, email):
        try:
            # Find user by email
            user = get_object_or_404(User, email=email)
            
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
                {'error': 'User with this email not found'},
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
    Mark one or multiple notifications as read
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = NotificationMarkReadSerializer(data=request.data)
        if serializer.is_valid():
            notification_ids = serializer.validated_data['notification_ids']
            
            # Update notifications for current user only
            updated_count = Notification.objects.filter(
                id__in=notification_ids,
                recipient=request.user,
                is_read=False
            ).update(is_read=True)
            
            return Response({
                'message': f'Marked {updated_count} notifications as read',
                'updated_count': updated_count
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationMarkAllReadView(APIView):
    """
    Mark all notifications as read for the current user
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({
            'message': f'Marked all {updated_count} notifications as read',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)


class NotificationUnreadCountView(APIView):
    """
    Get unread notification count for current user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return Response({
            'unread_count': unread_count
        }, status=status.HTTP_200_OK)