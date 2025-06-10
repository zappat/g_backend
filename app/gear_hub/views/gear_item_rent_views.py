from rest_framework import generics, permissions

from gear_hub.models import GearItemRent
from gear_hub.serializers import GearItemRentSerializer


class GearItemRentListCreateView(generics.ListCreateAPIView):
    queryset = GearItemRent.objects.all()
    serializer_class = GearItemRentSerializer
    permission_classes = (permissions.IsAuthenticated, )


class GearItemRentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GearItemRent.objects.all()
    serializer_class = GearItemRentSerializer
    permission_classes = (permissions.IsAuthenticated, )
