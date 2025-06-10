from datetime import datetime, timedelta

from django.db.models import Q
from django.db.models import Avg
from django.utils import timezone

from rest_framework import serializers

from gear_hub.models import GearItem, GearItemPicture, AddFavorite, Review, Booking, Cart
from user.serializers import UserSerializer


class GearItemPictureSerializer(serializers.ModelSerializer):
    """Serializer for gear item pictures with bulk support."""

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


class GearItemSerializer(serializers.ModelSerializer):
    """Serializer for gear items."""
    gear_item_pictures = GearItemPictureSerializer(source='gearitempicture_set', many=True, required=False)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    provider = UserSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)  
    category_name = serializers.SerializerMethodField(read_only=True) 
    booked_dates = serializers.SerializerMethodField(read_only=True)
    joining_date = serializers.SerializerMethodField(read_only=True)
    positive_review = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GearItem
        fields = (
            "id",
            "name",
            "description",
            "features",
            "rent_start_date",
            "rent_end_date",
            "category",
            "category_name",
            "provider",
            "gear_item_pictures",
            "is_favorite",
            "pick_up_location",
            "brand",
            "model",
            "replacement_value",
            "location_privacy",
            "status",
            "visibility",
            "promotion",
            "total_views",
            "value",
            "rentals",
            "average_rating", 
            "booked_dates",
            "joining_date",
            "positive_review"
        )

    def get_positive_review(self, obj):
        """Returns the percentage of the average rating"""
        rating = self.get_average_rating(obj=obj)
        if rating is None:
            return None
        postiive_review_percentage = (rating / 5) * 100
        return postiive_review_percentage

    def get_joining_date(self, obj):
        """Returns the joining date of the gear provider"""
        profile = getattr(obj.provider, "profile", None)
        if profile:
            return profile.created_at.date().isoformat()
        return None

    def get_booked_dates(self, obj):
        """ Returns all the booked dates for the gear item"""
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)

        bookings = Cart.objects.filter(
            gear_item=obj,
            pick_up_date__gte=start_of_month,
            drop_off_date__lte=end_of_month
        )

        booked_dates = set()
        for booking in bookings:
            current_date = booking.pick_up_date
            while current_date <= booking.drop_off_date:
                booked_dates.add(current_date.isoformat())
                current_date += timedelta(days=1)
        return list(booked_dates)

    def get_category_name(self, obj):
        """Returns the name of the category"""
        return obj.category.category_name if obj.category else None

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return AddFavorite.objects.filter(user=user, gear_item=obj).exists()
        return False


    def get_average_rating(self, obj):
        """Calculates the average rating for the gear item."""
        average = Review.objects.filter(gear_item=obj).aggregate(Avg('rating'))['rating__avg']
        return round(average, 2) if average else None


    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['provider'] = request.user
        gear_item_pictures_data = request.FILES.getlist('gear_item_pictures')

        gear_item = GearItem.objects.create(**validated_data)

        for picture_data in gear_item_pictures_data:
            GearItemPicture.objects.create(gear_item=gear_item, image=picture_data)

        return gear_item

    def update(self, instance, validated_data):
        request = self.context.get('request')
        gear_item_pictures_data = request.FILES.getlist('gear_item_pictures')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if gear_item_pictures_data:
            old_pictures = GearItemPicture.objects.filter(gear_item=instance)
            for old_picture in old_pictures:
                old_picture.image.delete(save=False)
                old_picture.delete()

            for picture_data in gear_item_pictures_data:
                GearItemPicture.objects.create(gear_item=instance, image=picture_data)

        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        pictures = GearItemPicture.objects.filter(gear_item=instance)
        representation['gear_item_pictures'] = GearItemPictureSerializer(pictures, many=True).data
        return representation
