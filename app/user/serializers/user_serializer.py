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
        fields = ('id', 'email', 'username', 'password', 'role', 'merchant_profile', 'renter_profile')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'username': {'read_only': True}  # Username is auto-generated
        }
    
    def create(self, validated_data):
        """Create a user and return access and refresh token."""
        print(f"🔍 UserSerializer.create() called with validated_data: {validated_data}")
        
        # Create user
        user = get_user_model().objects.create_user(**validated_data)
        print(f"🔍 User created: {user}")
        
        # Create profile based on role
        if user.role == 'merchant':
            from user.models import MerchantProfile
            profile, created = MerchantProfile.objects.get_or_create(user=user)
            print(f"🔍 MerchantProfile created: {profile}, created: {created}")
        elif user.role == 'renter':
            from user.models import RenterProfile
            profile, created = RenterProfile.objects.get_or_create(user=user)
            print(f"🔍 RenterProfile created: {profile}, created: {created}")
        
        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
        
        user.save()
        return user

