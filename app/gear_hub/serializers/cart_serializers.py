import json
from decimal import Decimal
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from gear_hub.serializers import GearItemSerializer
from gear_hub.models import Cart, GearItemRent, GearItem

class CartSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    gear_item = serializers.PrimaryKeyRelatedField(
        queryset=GearItem.objects.all(), write_only=True
    )

    gear_item_details = GearItemSerializer(
        source="gear_item", read_only=True
        )

    class Meta:
        model = Cart
        fields = (
            "id", "user", "gear_item", "pick_up_date", "drop_off_date",
            "has_booked", "quantity", "total_days", "gear_item_details",
            "total_days", "total_price"
        )

        read_only_fields = ("id", "user", "total_price", "has_booked", "total_days")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is None: 
            self.fields['gear_item'].required = True
        else:  
            self.fields['gear_item'].required = False



    def validate(self, data):
        """Ensure drop off date is after pickup date"""
        pick_up_date = data.get("pick_up_date") or (self.instance.pick_up_date if self.instance else None)
        drop_off_date = data.get("drop_off_date") or (self.instance.drop_off_date if self.instance else None)
        gear_item = data.get("gear_item") or (self.instance.gear_item if self.instance else None)

        if pick_up_date and drop_off_date:
            if pick_up_date > drop_off_date:
                raise serializers.ValidationError({
                    "dropoff_date": "Drop off date must be after pick up date"
                })
        gear_item_rent = get_object_or_404(GearItemRent, gear_item=gear_item)

        blocked_dates = json.loads(gear_item_rent.blocked_dates) if isinstance(gear_item_rent.blocked_dates, str) else gear_item_rent.blocked_dates

        booked_dates = set(
            (pick_up_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range((drop_off_date - pick_up_date).days + 1)
        )

        if any(date in booked_dates for date in blocked_dates):
            raise serializers.ValidationError({"blocked_dates":"Can't add the item in this duration."})

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        gear_item = validated_data.get("gear_item", None)
        pick_up_date = validated_data.get("pick_up_date")
        drop_off_date = validated_data.get("drop_off_date")
        quantity = validated_data.get("quantity", 0)

        if quantity == 0:
            raise serializers.ValidationError({"quantity":"Quantity can't be zero"})
    
        if not gear_item:
            raise serializers.ValidationError({"gear_item":"Gear item id is required"})

        gear_item_rent = get_object_or_404(GearItemRent, gear_item=gear_item)

        gear_quantity_available = gear_item_rent.qty - gear_item_rent.qty_rented

        if quantity > gear_quantity_available:
            raise serializers.ValidationError({"quantity":f"Can't book more than {gear_quantity_available}"})

        if pick_up_date and drop_off_date:
            total_days = (drop_off_date - pick_up_date).days
        else:
            total_days = 1

        validated_data["total_days"] = total_days
        validated_data["total_price"] = Decimal(quantity) * gear_item_rent.daily_rental_price * Decimal(total_days)

        cart = Cart.objects.create(**validated_data)

        return cart
    
    def update(self, instance ,validated_data):
        user = self.context["request"].user
        instance.pick_up_date =  validated_data.get("pick_up_date", instance.pick_up_date)
        instance.drop_off_date =  validated_data.get("drop_off_date", instance.drop_off_date)
        instance.quantity = validated_data.get("quantity", instance.quantity)
        gear_item = validated_data.get("gear_item", instance.gear_item)
        
        if user != instance.user:
            raise serializers.ValidationError({
                "user": "Invalid user"
            })

        gear_item_rent = get_object_or_404(GearItemRent, gear_item=gear_item)

        gear_quantity_available = gear_item_rent.qty - gear_item_rent.qty_rented

        if instance.quantity > gear_quantity_available:
            raise serializers.ValidationError({"quantity":f"Can't book more than {gear_quantity_available}"})

        if instance.pick_up_date and instance.drop_off_date :
            instance.total_days = (instance.drop_off_date - instance.pick_up_date).days
        else:
            instance.total_days = 1

        instance.total_price = Decimal(instance.total_days) * instance.quantity * gear_item_rent.daily_rental_price

        instance.save()
        return instance
    