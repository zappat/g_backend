from django.shortcuts import get_object_or_404
from rest_framework import serializers
from gear_hub.models import Booking, GearItemRent, Cart
from gear_hub.serializers.cart_serializers import CartSerializer


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Bookings."""

    user = serializers.PrimaryKeyRelatedField(
        source="cart.user", read_only=True
    )

    cart = CartSerializer(read_only=True) 
    cart_id = serializers.PrimaryKeyRelatedField(
        queryset=Cart.objects.all(), write_only=True
    )  

    status = serializers.ChoiceField(choices=Booking.BookingStatus.choices, required=False)

    class Meta: 
        model = Booking
        fields = ("id", "cart", "cart_id", "user", "total_price", "status" )
        read_only_fields = ("id", "user", "total_price")

    def create(self, validated_data):
        user = self.context["request"].user
        cart = validated_data.pop("cart_id")

        if not cart:
            raise serializers.ValidationError({"cart":"Cart id is required"})
        
        if cart.user != user:
            raise serializers.ValidationError({"user": "You can only book your own items"})

        if cart.has_booked:
            raise serializers.ValidationError({"has_booked": "The selected item has been booked"})

        # gear_item_rent = get_object_or_404(GearItemRent, gear_item=cart.gear_item)


        # if gear_item_rent.qty_rented + cart.quantity > gear_item_rent.qty:
        #     raise serializers.ValidationError({"stock": "Out of stock"})

        # gear_item_rent.qty_rented += cart.quantity
        # gear_item_rent.save()

        cart.save()

        validated_data["total_price"] = 0
        # booking = Booking.objects.create(cart=cart, total_price=total_price, **validated_data)
        booking = Booking.objects.create(cart=cart, **validated_data)

        return booking