from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Follow

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model."""

    follower_id = serializers.IntegerField(source='follower.id')
    following_id = serializers.IntegerField(source='following.id')
    mode = serializers.IntegerField(source='mode')

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'follower_id', 'following_id', 'mode', 'created_at']


class FollowCreateSerializer(serializers.Serializer):
    """Serializer for creating/updating follow relationships."""

    user = serializers.IntegerField(help_text='ID of the user to follow')
    mode = serializers.IntegerField(
        min_value=1,
        max_value=2,
        help_text='1 for renter following merchant, 2 for merchant following renter'
    )

    def validate_user(self, value):
        """Validate that the user exists."""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value

    def validate(self, attrs):
        """Validate the follow request."""
        user_id = attrs['user']
        mode = attrs['mode']
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        # Check if user is trying to follow themselves
        if request.user.id == user_id:
            raise serializers.ValidationError("Users cannot follow themselves.")

        # Get the target user
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Target user does not exist.")

        # Check if already following with the same mode
        if Follow.objects.filter(
            follower=request.user,
            following=target_user,
            mode=mode
        ).exists():
            raise serializers.ValidationError(f"You are already following this user in mode {mode}.")

        return attrs


class FollowListSerializer(serializers.ModelSerializer):
    """Serializer for listing followers/following."""

    id = serializers.IntegerField(source='following.id', read_only=True)
    email = serializers.EmailField(source='following.email', read_only=True)
    display_name = serializers.SerializerMethodField()
    mode = serializers.CharField(source='get_mode_display', read_only=True)
    mode_value = serializers.IntegerField(source='mode', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'email', 'display_name', 'mode', 'mode_value', 'created_at']

    def get_display_name(self, obj):
        """Get display name from user profile."""
        user = obj.following
        # Try to get merchant profile first, then renter profile
        if hasattr(user, 'merchantprofile'):
            return user.merchantprofile.display_name
        elif hasattr(user, 'renterprofile'):
            return user.renterprofile.display_name
        return user.email