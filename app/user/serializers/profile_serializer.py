from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from user.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the Profile object."""

    class Meta:
        model = Profile
        fields = ('id', 'first_name', 'last_name',  'profile_picture', 'cover_picture',
                  'dob', 'about', 'location', 'linkedin_url', 'personal_website_url')
    
    def validate(self, attrs):
        if Profile.objects.filter(user=self.context['request'].user).exists() and self.context['request'].method == "POST":
            raise ValidationError("User Profile already exists")
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context['request'].user
        profile = Profile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        profile_picture = validated_data.get('profile_picture', None)
        if profile_picture and instance.profile_picture:
            instance.profile_picture.delete(save=False)

        cover_picture = validated_data.get('cover_picture', None)
        if cover_picture and instance.cover_picture:
            instance.cover_picture.delete(save=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
