from rest_framework import generics, permissions

from user.serializers import ProfileSerializer
from user.models import Profile


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrive Update profile object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ProfileSerializer
    
    def get_object(self):
        return self.request.user.profile
    

class ProfileDeleteAPIView(generics.DestroyAPIView):
    """Delete profile object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
