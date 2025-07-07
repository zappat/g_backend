from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from gear_hub.serializers.gear_item_serializer import GearItemSerializer
from gear_hub.models import GearItem, GearCategories
from gear_hub.filters import GearItemFilter

from core.permission import IsAdminOrProvider
from core.pagination import StandardResultsSetPagination

class GearItemListAPIView(generics.ListAPIView):
    """Return list of gear items"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = GearItemSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = GearItem.objects.all()
        if self.request.user.is_authenticated:
            queryset = queryset.filter(owner=user)
        return queryset

class AvailableGearItemListAPIView(generics.ListAPIView):
    """Return list of gear items according to filtered search"""

    queryset = GearItem.objects.all()
    serializer_class = GearItemSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GearItemFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = (permissions.AllowAny,)


    def get_queryset(self):
        queryset = super().get_queryset().filter(location_privacy=GearItem.LocatiionPrivacy.PUBLIC).order_by('id')
        return queryset


class GearItemRetrieveAPIView(generics.RetrieveAPIView):
    """Return object of gear items"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = GearItemSerializer
    queryset = GearItem.objects.all()


    def get_related_items(self, gear_item):
        """Retrieve related gear item as suggestions while retrieving one gear item"""
        related_items = GearItem.objects.filter(
            owner=gear_item.owner,
        ).exclude(id=gear_item.id)[:4]

        if related_items.count() < 4:
            additional_items_needed = 4 - related_items.count()
            
            category_ids = GearCategories.objects.get(id=gear_item.equipment_category.id).get_all_category_ids()

            additional_items = GearItem.objects.filter(
                equipment_category__id__in = category_ids
            ).exclude(owner=gear_item.owner).exclude(id=gear_item.id)[:additional_items_needed]

            related_items = list(related_items) + list(additional_items)

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
    
    permission_classes = (IsAdminOrProvider,)
    serializer_class = GearItemSerializer
    queryset = GearItem.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, owner=self.request.user)


class GearItemUpdateApiView(generics.UpdateAPIView):
    """Update gear item object"""
    
    permission_classes = (IsAdminOrProvider,)
    serializer_class = GearItemSerializer
    queryset = GearItem.objects.all()


class GearItemDestroyAPIView(generics.DestroyAPIView):
    """Delete gear item object"""
    
    permission_classes = (IsAdminOrProvider,)
    serializer_class = GearItemSerializer
    queryset = GearItem.objects.all()
    

class GearItemBulkDestroyAPIView(APIView):
    """Bulk delete gear item objects"""

    def delete(self, request, ids):
        ids = ids.split(',')
        GearItem.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)