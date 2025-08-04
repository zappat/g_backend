from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth import get_user_model

from gear_hub.serializers import AddFavoriteSerializer
from gear_hub.models import AddFavorite, GearItem

User = get_user_model()


class AddFavoriteCreateApiView(generics.CreateAPIView):
    """Create add favorite gear object"""
    
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddFavoriteSerializer
    queryset = AddFavorite.objects.all()
    

class ListFavoriteApiView(generics.ListAPIView):
    """Retrieve all favorite gear object"""
    
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddFavoriteSerializer
    queryset = AddFavorite.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        return AddFavorite.objects.filter(user=user)
    

class AddFavoriteDestroyAPIView(generics.DestroyAPIView):
    """Delete add favorite gear object"""
    
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddFavoriteSerializer
    queryset = AddFavorite.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        gear_item_id = self.kwargs.get('gear_item_id')
        favorites = get_list_or_404(AddFavorite, user=user, gear_item_id=gear_item_id)
        
        for favorite in favorites:
            favorite.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddFavoriteByEmailAPIView(APIView):
    """Add gear item to user's favorite list using email and item ID"""
    
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, *args, **kwargs):
        """Add item to user's favorite list"""
        try:
            print(f"📝 Received request data: {request.data}")
            # Get email and item_id from request data
            email = request.data.get('email')
            item_id = request.data.get('item_id')
            
            print(f"📧 Email: {email}")
            print(f"🆔 Item ID: {item_id}")
            
            if not email:
                return Response(
                    {"error": "Email is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not item_id:
                return Response(
                    {"error": "Item ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": f"User with email '{email}' not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Find gear item by ID
            try:
                gear_item = GearItem.objects.get(id=item_id)
            except GearItem.DoesNotExist:
                return Response(
                    {"error": f"Gear item with ID '{item_id}' not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if already in favorites
            existing_favorite = AddFavorite.objects.filter(user=user, gear_item=gear_item).first()
            if existing_favorite:
                # Delete existing favorite (toggle off)
                favorite_id = str(existing_favorite.id)
                existing_favorite.delete()
                return Response(
                    {
                        "message": "Item removed from favorites",
                        "action": "removed",
                        "favorite_id": favorite_id,
                        "user_email": email,
                        "item_id": item_id
                    }, 
                    status=status.HTTP_200_OK
                )
            else:
                # Create new favorite (toggle on)
                favorite = AddFavorite.objects.create(user=user, gear_item=gear_item)
                return Response(
                    {
                        "message": "Item added to favorites successfully",
                        "action": "added",
                        "favorite_id": str(favorite.id),
                        "user_email": email,
                        "item_id": item_id
                    }, 
                    status=status.HTTP_201_CREATED
                )
            
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )