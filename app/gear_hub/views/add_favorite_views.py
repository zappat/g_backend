from rest_framework import generics, permissions, status
from rest_framework.response import Response

from django.shortcuts import get_list_or_404

from gear_hub.serializers import AddFavoriteSerializer
from gear_hub.models import AddFavorite


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