from rest_framework import serializers

from gear_hub.models import Review
from gear_hub.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Reviews."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = (
            'id',
            'user',
            'gear_item',
            'rating',
            'comment',
            'created_at',
        )
        extra_kwargs = {
            'created_at': {'read_only': True}
        }
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)