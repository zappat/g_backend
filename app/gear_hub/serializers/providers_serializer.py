from rest_framework import serializers

from user.models import MerchantProfile


class GearProviderSerializer(serializers.ModelSerializer):
    """Serializer for gear providers."""
    class Meta:
        model = MerchantProfile
        fields = '__all__'