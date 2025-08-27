from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from ..models import Follow
from ..serializers import FollowCreateSerializer, FollowListSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request):
    """
    Follow a user with specific mode.

    POST body should include Content-Type: application/json
    {
        "user": <user_id>,
        "mode": 1  // 1 for renter following merchant, 2 for merchant following renter
    }
    """
    serializer = FollowCreateSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        user_id = serializer.validated_data['user']
        mode = serializer.validated_data['mode']

        following_user = get_object_or_404(User, id=user_id)

        # Create follow relationship with specified mode
        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user,
            following=following_user,
            mode=mode,
            defaults={'mode': mode}
        )

        if created:
            mode_text = "renter following merchant" if mode == 1 else "merchant following renter"
            return Response({
                'message': f'You are now following {following_user.email} as {mode_text}',
                'following': True,
                'mode': mode
            }, status=status.HTTP_201_CREATED)
        else:
            mode_text = "renter following merchant" if mode == 1 else "merchant following renter"
            return Response({
                'message': f'You are already following this user as {mode_text}',
                'following': True,
                'mode': mode
            }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, user_id, mode):
    """
    Unfollow a user with specific mode.

    POST /api/follow/unfollow/<user_id>/<mode>/
    """
    try:
        following_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        follow_obj = Follow.objects.get(
            follower=request.user,
            following=following_user,
            mode=mode
        )
        follow_obj.delete()

        mode_text = "renter following merchant" if mode == 1 else "merchant following renter"
        return Response({
            'message': f'You have unfollowed {following_user.email} from {mode_text}',
            'following': False,
            'mode': mode
        }, status=status.HTTP_200_OK)
    except Follow.DoesNotExist:
        mode_text = "renter following merchant" if mode == 1 else "merchant following renter"
        return Response({
            'message': f'You are not following this user as {mode_text}',
            'following': False,
            'mode': mode
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_followers(request, user_id=None):
    """
    Get list of users following the current user or a specific user.

    If user_id is provided, get followers for that user.
    Otherwise, get followers for the current authenticated user.
    """
    if user_id:
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        followers = Follow.objects.filter(following=target_user)
        user_display = f"User {target_user.email}"
    else:
        followers = Follow.objects.filter(following=request.user)
        user_display = "You"

    serializer = FollowListSerializer(followers, many=True)
    return Response({
        'followers': serializer.data,
        'count': followers.count(),
        'user': user_display
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_following(request, user_id=None):
    """
    Get list of users that the current user or a specific user is following.

    If user_id is provided, get users that the specified user is following.
    Otherwise, get users that the current authenticated user is following.
    """
    if user_id:
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        following = Follow.objects.filter(follower=target_user)
        user_display = f"User {target_user.email}"
    else:
        following = Follow.objects.filter(follower=request.user)
        user_display = "You"

    serializer = FollowListSerializer(following, many=True)
    return Response({
        'following': serializer.data,
        'count': following.count(),
        'user': user_display
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def follow_status(request, user_id):
    """
    Check follow status with a specific user and return mode information.
    """
    try:
        following_user = User.objects.get(id=user_id)
        follows = Follow.objects.filter(
            follower=request.user,
            following=following_user
        )

        follow_modes = list(follows.values_list('mode', flat=True))

        return Response({
            'user_id': user_id,
            'is_following': len(follow_modes) > 0,
            'follow_modes': follow_modes,
            'following_as_renter': 1 in follow_modes,
            'following_as_merchant': 2 in follow_modes
        })
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )