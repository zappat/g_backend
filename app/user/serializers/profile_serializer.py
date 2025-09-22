from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from user.models import MerchantProfile, RenterProfile


class MerchantProfileSerializer(serializers.ModelSerializer):
    """Serializer for the MerchantProfile object."""

    equipment_categories = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = MerchantProfile
        fields = (
            'id', 'user', 'created_at', 'updated_at', 'profile_picture', 'cover_picture',
            'display_name', 'contact_email', 'location', 'website_url',
            'about', 'linkedin_url', 'instagram_url', 'equipment_categories',
            'is_pro', 'is_verified', 'pro_expires_at', 'views',
        )

    def validate(self, attrs):
        print(f"🔍 MerchantProfileSerializer.validate() called with attrs: {attrs}")
        print(f"🔍 Request method: {self.context['request'].method}")
        print(f"🔍 Request user: {self.context['request'].user}")
        
        # Only check for existing profile if we have a valid user and it's a POST request
        if hasattr(self.context['request'], 'user') and self.context['request'].user and not self.context['request'].user.is_anonymous:
            if MerchantProfile.objects.filter(user=self.context['request'].user).exists() and self.context['request'].method == "POST":
                raise ValidationError("Merchant Profile already exists")
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context['request'].user
        profile = MerchantProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        print(f"🔍 MerchantProfileSerializer.update() called with validated_data: {validated_data}")
        
        # Handle delete_profile_picture from request data
        request_data = self.context['request'].data
        delete_profile_picture = request_data.get('delete_profile_picture', False)
        
        # Convert string to boolean if needed
        if isinstance(delete_profile_picture, str):
            delete_profile_picture = delete_profile_picture.lower() in ['true', '1', 'yes', 'on']
        
        if delete_profile_picture:
            print(f"🔍 Deleting profile picture for user {instance.user.id}")
            # Delete the current profile picture if it exists and is not default
            if instance.profile_picture and instance.profile_picture.name != 'profile-photo/default.png':
                instance.profile_picture.delete(save=False)
            # Set profile picture to default
            instance.profile_picture = 'profile-photo/default.png'
        
        # Handle regular profile picture update
        profile_picture = validated_data.get('profile_picture', None)
        if profile_picture and instance.profile_picture and instance.profile_picture.name != 'profile-photo/default.png':
            instance.profile_picture.delete(save=False)

        cover_picture = validated_data.get('cover_picture', None)
        if cover_picture and instance.cover_picture and instance.cover_picture.name != 'cover-photo/default.png':
            instance.cover_picture.delete(save=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RenterProfileSerializer(serializers.ModelSerializer):
    """Serializer for the RenterProfile object."""

    class Meta:
        model = RenterProfile
        fields = ('id', 'user', 'created_at', 'updated_at', 'profile_picture', 'cover_picture',
                  'display_name', 'company_name', 'location', 'about',
                  'website_url', 'linkedin_url', 'instagram_url', 'vimeo_url', 'youtube_url')

    def validate(self, attrs):
        # Only check for existing profile if we have a valid user and it's a POST request
        if hasattr(self.context['request'], 'user') and self.context['request'].user and not self.context['request'].user.is_anonymous:
            if RenterProfile.objects.filter(user=self.context['request'].user).exists() and self.context['request'].method == "POST":
                raise ValidationError("Renter Profile already exists")
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context['request'].user
        profile = RenterProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        # Handle delete_profile_picture from request data
        request_data = self.context['request'].data
        delete_profile_picture = request_data.get('delete_profile_picture', False)
        
        # Convert string to boolean if needed
        if isinstance(delete_profile_picture, str):
            delete_profile_picture = delete_profile_picture.lower() in ['true', '1', 'yes', 'on']
        
        print("delete_profile_picture", delete_profile_picture)
        if delete_profile_picture:
            print(f"🔍 Deleting profile picture for user {instance.user.id}")
            # Delete the current profile picture if it exists and is not default
            if instance.profile_picture and instance.profile_picture.name != 'profile-photo/default.png':
                instance.profile_picture.delete(save=False)
            # Set profile picture to default
            instance.profile_picture = 'profile-photo/default.png'
        
        # Handle regular profile picture update
        profile_picture = validated_data.get('profile_picture', None)
        if profile_picture and instance.profile_picture and instance.profile_picture.name != 'profile-photo/default.png':
            instance.profile_picture.delete(save=False)

        cover_picture = validated_data.get('cover_picture', None)
        if cover_picture and instance.cover_picture and instance.cover_picture.name != 'cover-photo/default.png':
            instance.cover_picture.delete(save=False)
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
