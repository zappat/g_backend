from django.urls import path
from .views import (
    NotificationsByEmailView,
    NotificationListCreateView,
    NotificationDetailView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
)

urlpatterns = [
    # Main endpoint: get notifications by email
    path('notifications/<str:email>/', NotificationsByEmailView.as_view(), name='notifications-by-email'),
    
    # CRUD operations
    path('notifications/', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/detail/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    
    # Utility endpoints
    path('notifications/mark-read/<int:pk>/', NotificationMarkReadView.as_view(), name='notification-mark-read-single'),
    path('notifications/mark-read/all/', NotificationMarkAllReadView.as_view(), name='notification-mark-read-all'),
]