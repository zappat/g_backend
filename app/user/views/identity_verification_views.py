from rest_framework import generics, permissions

from user.serializers import IdentityVerificationSerializer
from user.models import IdentityVerification


class IdentityVerificationCreateAPIView(generics.CreateAPIView):
    """Save user identity documents."""

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = IdentityVerificationSerializer
    queryset = IdentityVerification.objects.all()
    

class IdentityVerificationRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrive and Update Identity Verification object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = IdentityVerificationSerializer
    queryset = IdentityVerification.objects.all()
    

class IdentityVerificationDeleteAPIView(generics.DestroyAPIView):
    """Delete Identity Verification object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = IdentityVerificationSerializer
    queryset = IdentityVerification.objects.all()
    