from rest_framework import serializers
from .models import Review
from core.models import User
from rfq.models import RFQ
from user.models import MerchantProfile

class ReviewSerializer(serializers.ModelSerializer):
    renter = serializers.PrimaryKeyRelatedField(read_only=True)
    merchant = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    rfq = serializers.PrimaryKeyRelatedField(queryset=RFQ.objects.all(), required=False)
    
    # Add support for frontend field names
    merchant_id = serializers.UUIDField(write_only=True, required=False)
    rfq_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Review
        fields = [
            'id', 'renter', 'merchant', 'rfq', 'rating', 'text', 'would_work_again', 'created_at', 'updated_at',
            'merchant_id', 'rfq_id'  # Add frontend field names
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

    def validate(self, attrs):
        # Handle frontend field names during validation
        merchant_id = attrs.pop('merchant_id', None)
        rfq_id = attrs.pop('rfq_id', None)
        
        # Map frontend field names to backend field names
        if merchant_id:
            try:
                merchant_profile = MerchantProfile.objects.get(id=merchant_id)
                attrs['merchant'] = merchant_profile.user  # Get the User from the MerchantProfile
            except MerchantProfile.DoesNotExist:
                raise serializers.ValidationError({'merchant_id': 'Merchant profile not found'})
        elif not attrs.get('merchant'):
            raise serializers.ValidationError({'merchant': 'This field is required.'})
        
        if rfq_id:
            try:
                attrs['rfq'] = RFQ.objects.get(id=rfq_id)
            except RFQ.DoesNotExist:
                raise serializers.ValidationError({'rfq_id': 'RFQ not found'})
        elif not attrs.get('rfq'):
            raise serializers.ValidationError({'rfq': 'This field is required.'})
        
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data) 