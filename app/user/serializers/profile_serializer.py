from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from user.models import MerchantProfile, RenterProfile


class MerchantProfileSerializer(serializers.ModelSerializer):
    """Serializer for the MerchantProfile object."""

    class Meta:
        model = MerchantProfile
        fields = ('id', 'user', 'profile_picture', 'cover_picture',
                  'display_name', 'contact_email', 'location', 'website_url',
                  'about', 'linkedin_url', 'instagram_url', 'equipment_categories')

    def validate(self, attrs):
        if MerchantProfile.objects.filter(user=self.context['request'].user).exists() and self.context['request'].method == "POST":
            raise ValidationError("Merchant Profile already exists")
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context['request'].user
        profile = MerchantProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
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
        fields = ('id', 'user', 'profile_picture', 'cover_picture',
                  'display_name', 'company_name', 'location', 'about',
                  'website_url', 'linkedin_url', 'instagram_url', 'vimeo_url', 'youtube_url')

    def validate(self, attrs):
        if RenterProfile.objects.filter(user=self.context['request'].user).exists() and self.context['request'].method == "POST":
            raise ValidationError("Renter Profile already exists")
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context['request'].user
        profile = RenterProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
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
