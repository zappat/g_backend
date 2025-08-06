from rest_framework import generics, permissions, status
from rest_framework.response import Response

from user.serializers import MerchantProfileSerializer, RenterProfileSerializer
from user.models import MerchantProfile, RenterProfile


class MerchantProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve Update merchant profile object"""
    
    permission_classes = (permissions.AllowAny, )  # Temporarily allow all access
    serializer_class = MerchantProfileSerializer
    
    def get_object(self):
        if not self.request.user.is_authenticated:
            # Return a default merchant profile or raise an error
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must be authenticated to access merchant profile")
        return self.request.user.merchantprofile
    
    def update(self, request, *args, **kwargs):
        try:
            print(f"📝 Merchant profile update - Received data: {request.data}")
            print(f"📝 Request user: {request.user}")
            print(f"📝 Request authenticated: {request.user.is_authenticated}")
            serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
            if not serializer.is_valid():
                print(f"❌ Merchant profile validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            print(f"✅ Merchant profile data is valid")
            return super().update(request, *args, **kwargs)
        except Exception as e:
            print(f"❌ Merchant profile update error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MerchantProfileDeleteAPIView(generics.DestroyAPIView):
    """Delete merchant profile object"""
    
    permission_classes = (permissions.AllowAny, )  # Temporarily allow all access
    serializer_class = MerchantProfileSerializer
    queryset = MerchantProfile.objects.all()


class RenterProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve Update renter profile object"""
    
    permission_classes = (permissions.AllowAny, )  # Temporarily allow all access
    serializer_class = RenterProfileSerializer
    
    def get_object(self):
        if not self.request.user.is_authenticated:
            # Return a default renter profile or raise an error
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must be authenticated to access renter profile")
        return self.request.user.renterprofile
    

class RenterProfileDeleteAPIView(generics.DestroyAPIView):
    """Delete renter profile object"""
    
    permission_classes = (permissions.AllowAny, )  # Temporarily allow all access
    serializer_class = RenterProfileSerializer
    queryset = RenterProfile.objects.all()
