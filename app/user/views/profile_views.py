from rest_framework import generics, permissions

from user.serializers import MerchantProfileSerializer, RenterProfileSerializer
from user.models import MerchantProfile, RenterProfile


class MerchantProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve Update merchant profile object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MerchantProfileSerializer
    
    def get_object(self):
        return self.request.user.merchantprofile
    

class MerchantProfileDeleteAPIView(generics.DestroyAPIView):
    """Delete merchant profile object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MerchantProfileSerializer
    queryset = MerchantProfile.objects.all()


class RenterProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve Update renter profile object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RenterProfileSerializer
    
    def get_object(self):
        return self.request.user.renterprofile
    

class RenterProfileDeleteAPIView(generics.DestroyAPIView):
    """Delete renter profile object"""
    
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RenterProfileSerializer
    queryset = RenterProfile.objects.all()
