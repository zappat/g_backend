from django.contrib.auth import get_user_model
from django.db.models import Avg

from rest_framework import serializers
from review.models import Review

from user.serializers.profile_serializer import MerchantProfileSerializer, RenterProfileSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    merchant_profile = MerchantProfileSerializer(read_only=True)
    renter_profile = RenterProfileSerializer(read_only=True)

    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=['merchant', 'renter']),
        required=False,
        write_only=True
    )

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'password', 'role', 'roles', 'merchant_profile', 'renter_profile')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'role': {'read_only': True}  # Make legacy role field read-only
        }
    
    def create(self, validated_data):
        """Create a user and return access and refresh token."""
        # Extract roles from validated data
        roles = validated_data.pop('roles', ['renter'])  # Default to ['renter'] if not provided
        
        # Set the legacy role field to the first role
        validated_data['role'] = roles[0] if roles else 'renter'
        
        # Create user
        user = get_user_model().objects.create_user(**validated_data)
        
        # Set the new roles field
        user.roles = roles
        user.save()
        
        # Create profiles based on roles
        if 'merchant' in roles:
            from user.models import MerchantProfile
            MerchantProfile.objects.get_or_create(user=user)
        if 'renter' in roles:
            from user.models import RenterProfile
            RenterProfile.objects.get_or_create(user=user)
        
        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

