from rest_framework import serializers
from gear_hub.models import GearItemRent


class GearItemRentSerializer(serializers.ModelSerializer):

    class Meta:
        model = GearItemRent
        fields = (
            'id',
            'details',
            'included_accessories',
            'daily_rental_price',
            'qty',
            'blocked_dates', 
            'gear_item',
            'created_at',
            'updated_at'
        )
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            }
