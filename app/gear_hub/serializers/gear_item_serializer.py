from datetime import datetime, timedelta

from django.db.models import Q
from django.db.models import Avg
from django.utils import timezone

from rest_framework import serializers

from gear_hub.models import GearItem, GearItemPicture, AddFavorite, GearCategories
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


class GearCategoriesSerializer(serializers.ModelSerializer):
    """Serializer for gear categories."""
    class Meta:
        model = GearCategories
        fields = ('id', 'category_name')


class GearItemSerializer(serializers.ModelSerializer):
    """Serializer for gear items."""
    gear_item_pictures = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    is_favorite = serializers.SerializerMethodField(read_only=True)
    equipment_category = serializers.CharField(write_only=True, required=False)
    provider = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = GearItem
        fields = (
            "id",
            "equipment_name",
            "equipment_category",
            "provider",
            "key_specifications",
            "additional_notes",
            "is_public",
            "pick_up_location",
            "location_privacy",
            "gear_item_pictures",
            "is_favorite",
        )

    def to_representation(self, instance):
        """Custom representation to include gear_item_pictures, equipment_category, and provider for read operations."""
        data = super().to_representation(instance)
        # Add gear_item_pictures for read operations
        pictures = instance.gearitempicture_set.all()
        data['gear_item_pictures'] = GearItemPictureSerializer(pictures, many=True, context=self.context).data
        # Add equipment_category details for read operations
        if instance.equipment_category:
            data['equipment_category'] = GearCategoriesSerializer(instance.equipment_category, context=self.context).data
        # Add provider details for read operations
        if instance.provider:
            data['provider'] = UserSerializer(instance.provider, context=self.context).data
        return data

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return AddFavorite.objects.filter(user=user, gear_item=obj).exists()
        return False

    def create(self, validated_data):
        gear_item_pictures = validated_data.pop('gear_item_pictures', [])
        equipment_category_name = validated_data.pop('equipment_category', None)
        provider_name = validated_data.pop('provider', None)
        
        # Handle equipment category conversion
        if equipment_category_name:
            try:
                equipment_category = GearCategories.objects.get(category_name__iexact=equipment_category_name)
                validated_data['equipment_category'] = equipment_category
            except GearCategories.DoesNotExist:
                raise serializers.ValidationError({"equipment_category": f"Category '{equipment_category_name}' does not exist"})
        
        # Handle provider from frontend
        if provider_name:
            try:
                from user.models import MerchantProfile
                merchant_profile = MerchantProfile.objects.get(display_name__iexact=provider_name)
                validated_data['provider'] = merchant_profile.user  # Get the User instance
            except MerchantProfile.DoesNotExist:
                raise serializers.ValidationError({"provider": f"User with name '{provider_name}' does not exist"})
        
        # Create the gear item
        gear_item = super().create(validated_data)
        
        # Handle gear item pictures
        for i, photo in enumerate(gear_item_pictures):
            GearItemPicture.objects.create(
                gear_item=gear_item,
                image=photo,
                is_cover_photo=(i == 0)  # First photo is cover photo
            )
        
        return gear_item
