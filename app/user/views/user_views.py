"""Views for the user APIs"""
from django.contrib.auth import get_user_model

from rest_framework import (generics, permissions, status)
from rest_framework.response import Response
from user.serializers import UserSerializer
from user.utils import get_tokens_for_user


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        instance = super(CreateUserView, self).post(request, *args, **kwargs)
        email = instance.data.get('email')
        user = get_user_model().objects.get(email=email)
        token = get_tokens_for_user(user)

        return Response(token, status=status.HTTP_201_CREATED)



class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return authenticated user."""
        return self.request.user


class UserDeleteApiView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = get_user_model().objects.all()