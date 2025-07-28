from rest_framework import generics, permissions, exceptions

from gear_hub.serializers import GearProviderSerializer
from user.models import MerchantProfile


class GearProvidersListAPIView(generics.ListAPIView):
    """Return list of gear categories"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = GearProviderSerializer

    def get_queryset(self):
        provider_id = self.request.query_params.get('provider_id')

        if provider_id:
            try:
                return MerchantProfile.objects.filter(id=provider_id)
            except MerchantProfile.DoesNotExist:
                raise exceptions.ValidationError("Provider with the provided ID does not exist.")
        else:
            return MerchantProfile.objects.all()
