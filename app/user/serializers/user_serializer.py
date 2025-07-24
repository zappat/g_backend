from django.contrib.auth import get_user_model
from django.db.models import Avg

from rest_framework import serializers
from review.models import Review

from user.serializers.profile_serializer import MerchantProfileSerializer, RenterProfileSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    merchant_profile = MerchantProfileSerializer(read_only=True)
    renter_profile = RenterProfileSerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id','email', 'password', 'role', 'merchant_profile', 'renter_profile')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
    
    def create(self, validated_data):
        """Create a user and return access and refresh token."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

