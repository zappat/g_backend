from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from gear_hub.serializers.gear_item_serializer import GearItemSerializer
from gear_hub.models import GearItem, GearCategories

from core.permission import IsAdminOrProvider
from core.pagination import StandardResultsSetPagination

class GearItemListAPIView(generics.ListAPIView):
    """Return list of gear items"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = GearItemSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        # Return all gear items, not filtered by provider
        queryset = GearItem.objects.all().order_by('-created_at') 
        return queryset
    
    def get_serializer_context(self):
        """Add request to serializer context for is_favorite calculation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class AvailableGearItemListAPIView(generics.ListAPIView):
    """Return list of gear items according to filtered search"""

    queryset = GearItem.objects.all()
    serializer_class = GearItemSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination
    permission_classes = (permissions.AllowAny,)


    def get_queryset(self):
        queryset = super().get_queryset().filter(location_privacy=GearItem.LocatiionPrivacy.PUBLIC).order_by('-created_at') 
        return queryset
    
    def get_serializer_context(self):
        """Add request to serializer context for is_favorite calculation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class GearItemRetrieveAPIView(generics.RetrieveAPIView):
    """Return object of gear items"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = GearItemSerializer
    queryset = GearItem.objects.all()
    
    def get_serializer_context(self):
        """Add request to serializer context for is_favorite calculation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


    def get_related_items(self, gear_item):
        """Retrieve related gear item as suggestions while retrieving one gear item"""
        # Get related items by the same category
        related_items = GearItem.objects.filter(
            equipment_category=gear_item.equipment_category
        ).exclude(id=gear_item.id)[:4]

        return related_items

    def retrieve(self,request, *args, **kwargs):
        instance = self.get_object() # id from params
        serializer = self.get_serializer(instance)

        related_items = self.get_related_items(instance)
        related_items_serializer = self.get_serializer(related_items, many=True)

        response_data = serializer.data
        response_data["related_items"] = related_items_serializer.data
    
        return Response(response_data)


class GearItemCreateApiView(generics.CreateAPIView):
    """Create gear item object"""
    
    permission_classes = (permissions.AllowAny,)
    serializer_class = GearItemSerializer
    queryset = GearItem.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save()


class GearItemUpdateApiView(generics.UpdateAPIView):
    """Update gear item object"""
    
    permission_classes = (permissions.AllowAny,)  # Require authentication
    serializer_class = GearItemSerializer
    queryset = GearItem.objects.all()


class GearItemDestroyAPIView(generics.DestroyAPIView):
    """Delete gear item object"""
    
    permission_classes = (permissions.AllowAny,)  # Require authentication
    serializer_class = GearItemSerializer
    queryset = GearItem.objects.all()
    

class GearItemBulkDestroyAPIView(APIView):
    """Bulk delete gear item objects"""

    def delete(self, request, ids):
        ids = ids.split(',')
        GearItem.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class GearItemToggleVisibilityAPIView(generics.UpdateAPIView):
    """Toggle visibility of gear item"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = GearItemSerializer
    queryset = GearItem.objects.all()

    def patch(self, request, *args, **kwargs):
        gear_item = self.get_object()
        gear_item.is_public = not gear_item.is_public
        gear_item.save()
        return Response(status=status.HTTP_200_OK)