import os
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    """
    Generates refresh and access tokens for the given user.

    Args:
        user: The user object for whom the tokens are generated.

    Returns:
        A dictionary containing the refresh and access tokens as strings.

    Examples:
        >>> user = User.objects.get(username='example_user')
        >>> tokens = get_tokens_for_user(user)
        >>> tokens
        {'refresh': '...', 'access': '...'}
    """

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



def get_upload_path(instance, filename):
    """return file upload path for user-identity"""
    return f'user-identity/{instance.user.id}/{filename}'

def get_gear_items_picture_path(instance, filename):
    """return file upload path for gear items pictures"""
    return f'gear-items-picture/{instance.gear_item.id}/{filename}'

def profile_picture_path(instance, filename):
    """return profile picture path"""
    return f'profile-picture/{instance.id}/{filename}'


def cover_picture_path(instance, filename):
    """return cover picture path"""
    return f'cover-picture/{instance.id}/{filename}'