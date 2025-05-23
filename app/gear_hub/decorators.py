from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def is_provider(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if request.user.role == 'gear_provider':
            # If user is a gear provider, allow the request to proceed
            return func(self, request, *args, **kwargs)
        else:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    return wrapper