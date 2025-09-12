from django.urls import path
from .views import follow_user, unfollow_user, list_followers, list_following, follow_status

app_name = 'follow'

urlpatterns = [
    path('follow/', follow_user, name='follow-user'),
    path('unfollow/<int:user_id>/<int:mode>/', unfollow_user, name='unfollow-user'),

    # List followers of specific user
    path('followers/<int:user_id>/', list_followers, name='list-followers-user'),

    # List users that specific user is following
    path('following/<int:user_id>/', list_following, name='list-following-user'),

    # Check follow status with a specific user
    path('status/<int:user_id>/', follow_status, name='follow-status'),
]