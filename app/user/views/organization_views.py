from rest_framework import generics, permissions

from user.serializers import OrganizationSerializer
from user.models import Organization


class OrganizationCreateAPIView(generics.CreateAPIView):
    """Create a new organization associated to user."""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()


class OrganizationRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrive and Update organization object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    

class OrganizationDeleteAPIView(generics.DestroyAPIView):
    """Delete organization object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
