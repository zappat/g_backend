from rest_framework import generics

from gear_hub.serializers import GearItemPictureSerializer
from gear_hub.models import GearItemPicture

from core.permission import IsAdminOrProvider


class GearItemPictureCreateApiView(generics.CreateAPIView):
    """Create gear item object"""
    
    permission_classes = (IsAdminOrProvider,)
    serializer_class = GearItemPictureSerializer
    queryset = GearItemPicture.objects.all()
    

class GearItemPictureUpdateApiView(generics.UpdateAPIView):
    """Update gear item object"""
    
    permission_classes = (IsAdminOrProvider,)
    serializer_class = GearItemPictureSerializer
    queryset = GearItemPicture.objects.all()


class GearItemPictureDestroyAPIView(generics.DestroyAPIView):
    """Delete gear item object"""
    
    permission_classes = (IsAdminOrProvider,)
    serializer_class = GearItemPictureSerializer
    queryset = GearItemPicture.objects.all()
