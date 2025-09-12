from rest_framework import generics, permissions
from user.models import EquipmentCategory
from user.serializers.equipment_category_serializer import EquipmentCategorySerializer


class EquipmentCategoryListAPIView(generics.ListAPIView):
    """Return list of equipment categories"""
    
    permission_classes = (permissions.AllowAny,)
    serializer_class = EquipmentCategorySerializer
    queryset = EquipmentCategory.objects.all().order_by('name')


class EquipmentCategoryDetailAPIView(generics.RetrieveAPIView):
    """Return specific equipment category"""
    
    permission_classes = (permissions.AllowAny,)
    serializer_class = EquipmentCategorySerializer
    queryset = EquipmentCategory.objects.all() 