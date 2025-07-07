from django.contrib.auth import get_user_model
from django.db.models import Avg

from rest_framework import serializers

from user.serializers.organization_serializer import OrganizationSerializer
from user.serializers.profile_serializer import MerchantProfileSerializer, RenterProfileSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    organization = OrganizationSerializer(read_only=True)
    merchant_profile = MerchantProfileSerializer(read_only=True)
    renter_profile = RenterProfileSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id','email', 'password', 'role', 'organization', 'merchant_profile', 'renter_profile', 'average_rating')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
        
    def get_average_rating(self, obj):
        """Calculates the average rating for the gear item."""
        average = Review.objects.filter(user=obj).aggregate(Avg('rating'))['rating__avg']
        return round(average, 2) if average else None
    
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

