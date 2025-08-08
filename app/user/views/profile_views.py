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
        
        # Try to get the merchant profile, create one if it doesn't exist
        try:
            return self.request.user.merchantprofile
        except MerchantProfile.DoesNotExist:
            # Create a new merchant profile for the user
            return MerchantProfile.objects.create(user=self.request.user)
    
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
        
        # Try to get the renter profile, create one if it doesn't exist
        try:
            print("Incoming data for ", self.request.user.renterprofile)
            return self.request.user.renterprofile
        except RenterProfile.DoesNotExist:
            # Create a new renter profile for the user
            return RenterProfile.objects.create(user=self.request.user)
    

class RenterProfileDetailAPIView(generics.RetrieveAPIView):
    """Get renter profile by user ID"""
    
    permission_classes = (permissions.AllowAny,)
    serializer_class = RenterProfileSerializer
    queryset = RenterProfile.objects.all()
    
    def get_object(self):
        """Get renter profile by user ID from URL parameter"""
        user_id = self.kwargs.get('pk')
        if not user_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("User ID is required")
        
        try:
            # Get the user first
            from core.models import User
            user = User.objects.get(id=user_id)
            
            # Try to get the renter profile, create one if it doesn't exist
            try:
                return user.renterprofile
            except RenterProfile.DoesNotExist:
                # Create a new renter profile for the user
                return RenterProfile.objects.create(user=user)
                
        except User.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("User not found")


class RenterProfileDeleteAPIView(generics.DestroyAPIView):
    """Delete renter profile object"""
    
    permission_classes = (permissions.AllowAny, )  # Temporarily allow all access
    serializer_class = RenterProfileSerializer
    queryset = RenterProfile.objects.all()
