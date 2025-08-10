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
        print(f"🔍 Checking is_favorite for gear item: {obj.id}")
        print(f"🔍 Request context: {request}")
        
        if request and hasattr(request, "user"):
            user = request.user
            print(f"🔍 User: {user}")
            print(f"🔍 User authenticated: {user.is_authenticated}")
            print(f"🔍 User ID: {getattr(user, 'id', 'No ID')}")
            
            if user.is_authenticated:
                is_fav = AddFavorite.objects.filter(user=user, gear_item=obj).exists()
                print(f"🔍 Is favorite: {is_fav}")
                return is_fav
            else:
                print(f"🔍 User not authenticated")
        else:
            print(f"🔍 No request or user in context")
        
        print(f"🔍 Returning False for is_favorite")
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

    def update(self, instance, validated_data):
        # Handle potential non-model fields first
        new_pictures = validated_data.pop('gear_item_pictures', None)

        # Resolve equipment_category from various frontend formats
        equipment_input = validated_data.pop('equipment_category', None)
        if equipment_input is not None:
            resolved_category = None

            # If dict provided
            if isinstance(equipment_input, dict):
                candidate_id = equipment_input.get('id')
                candidate_name = equipment_input.get('name') or equipment_input.get('category_name')

                if candidate_id and not resolved_category:
                    try:
                        resolved_category = GearCategories.objects.get(id=candidate_id)
                    except GearCategories.DoesNotExist:
                        resolved_category = None

                if candidate_name and not resolved_category:
                    resolved_category = GearCategories.objects.filter(
                        category_name__iexact=candidate_name
                    ).first()

                if candidate_id and not resolved_category:
                    try:
                        from user.models import EquipmentCategory
                        user_cat = EquipmentCategory.objects.get(pk=candidate_id)
                        resolved_category = GearCategories.objects.filter(
                            category_name__iexact=user_cat.name
                        ).first()
                    except Exception:
                        resolved_category = None

            # If string provided (UUID, numeric id from user EquipmentCategory, or name)
            elif isinstance(equipment_input, str):
                try:
                    from uuid import UUID
                    UUID(equipment_input)
                    resolved_category = GearCategories.objects.get(id=equipment_input)
                except Exception:
                    if equipment_input.isdigit():
                        try:
                            from user.models import EquipmentCategory
                            user_cat = EquipmentCategory.objects.get(pk=int(equipment_input))
                            resolved_category = GearCategories.objects.get(
                                category_name__iexact=user_cat.name
                            )
                        except Exception:
                            resolved_category = None
                    else:
                        try:
                            resolved_category = GearCategories.objects.get(
                                category_name__iexact=equipment_input
                            )
                        except GearCategories.DoesNotExist:
                            resolved_category = None

            # If integer provided (likely user EquipmentCategory id)
            elif isinstance(equipment_input, int):
                try:
                    from user.models import EquipmentCategory
                    user_cat = EquipmentCategory.objects.get(pk=equipment_input)
                    resolved_category = GearCategories.objects.get(
                        category_name__iexact=user_cat.name
                    )
                except Exception:
                    resolved_category = None

            if not resolved_category:
                raise serializers.ValidationError({
                    "equipment_category": "Invalid equipment_category. Provide a valid GearCategories id, name, or a user EquipmentCategory id that maps by name."
                })

            validated_data['equipment_category'] = resolved_category

        # Resolve provider from various frontend formats
        provider_input = validated_data.pop('provider', None)
        if provider_input is not None:
            resolved_provider = None

            try:
                from core.models import User
                from user.models import MerchantProfile
            except Exception:
                User = None
                MerchantProfile = None

            if isinstance(provider_input, dict):
                candidate_id = provider_input.get('id')
                candidate_email = provider_input.get('email')
                candidate_display = provider_input.get('display_name') or provider_input.get('name')

                if candidate_id and User and not resolved_provider:
                    resolved_provider = User.objects.filter(pk=candidate_id).first()
                if candidate_email and User and not resolved_provider:
                    resolved_provider = User.objects.filter(email__iexact=candidate_email).first()
                if candidate_display and MerchantProfile and not resolved_provider:
                    merchant_profile = MerchantProfile.objects.filter(display_name__iexact=candidate_display).first()
                    resolved_provider = getattr(merchant_profile, 'user', None)

            elif isinstance(provider_input, (int,)) and User:
                resolved_provider = User.objects.filter(pk=provider_input).first()

            elif isinstance(provider_input, str):
                if provider_input.isdigit() and User:
                    resolved_provider = User.objects.filter(pk=int(provider_input)).first()
                elif User:
                    # try email first
                    resolved_provider = User.objects.filter(email__iexact=provider_input).first()
                    if not resolved_provider and MerchantProfile:
                        merchant_profile = MerchantProfile.objects.filter(display_name__iexact=provider_input).first()
                        resolved_provider = getattr(merchant_profile, 'user', None)

            if not resolved_provider:
                raise serializers.ValidationError({
                    "provider": "Invalid provider. Provide a valid user id, email, or merchant display name."
                })

            validated_data['provider'] = resolved_provider

        # Perform the update
        instance = super().update(instance, validated_data)

        # If new pictures are provided, replace all existing pictures with the new set
        if new_pictures:
            # Delete all existing pictures for this gear item
            GearItemPicture.objects.filter(gear_item=instance).delete()

            # Create the new picture set; first photo becomes the cover photo
            for index, photo in enumerate(new_pictures):
                GearItemPicture.objects.create(
                    gear_item=instance,
                    image=photo,
                    is_cover_photo=(index == 0)
                )

        return instance
