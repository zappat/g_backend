from datetime import datetime, timedelta

from django.db.models import Q
from django.db.models import Avg
from django.utils import timezone

from rest_framework import serializers

from gear_hub.models import GearItem, GearItemPicture, AddFavorite
from user.serializers import UserSerializer


class GearItemPictureSerializer(serializers.ModelSerializer):
    """Serializer for gear item pictures with bulk support."""
    image = serializers.SerializerMethodField()

    class Meta:
        model = GearItemPicture
        fields = (
            "id",
            "image",
            "is_cover_photo",
            "gear_item"
        )
        extra_kwargs = {
            'gear_item': {'read_only': True}
        }

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class GearItemSerializer(serializers.ModelSerializer):
    """Serializer for gear items."""
    gear_item_pictures = GearItemPictureSerializer(source='gearitempicture_set', many=True, required=False)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    provider = UserSerializer(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GearItem
        fields = (
            "id",
            "equipment_name",
            "equipment_category",
            "key_specifications",
            "additional_notes",
            "description",
            "is_public",
            "pick_up_location",
            "location_privacy",
            "rentals",
            "gear_item_pictures",
        )

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return AddFavorite.objects.filter(user=user, gear_item=obj).exists()
        return False
