from rest_framework import serializers
from .models import Review
from core.models import User
from rfq.models import RFQ

class ReviewSerializer(serializers.ModelSerializer):
    renter = serializers.PrimaryKeyRelatedField(read_only=True)
    merchant = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    rfq = serializers.PrimaryKeyRelatedField(queryset=RFQ.objects.all())

    class Meta:
        model = Review
        fields = [
            'id', 'renter', 'merchant', 'rfq', 'rating', 'text', 'would_work_again', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'renter', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value

    def validate_text(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError('Review must be at least 20 characters long.')
        return value 