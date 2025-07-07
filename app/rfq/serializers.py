from rest_framework import serializers
from .models import RFQ, RFQAttachment
from user.models import EquipmentCategory

class RFQAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQAttachment
        fields = ['id', 'rfq', 'file', 'uploaded_at']

class RFQSerializer(serializers.ModelSerializer):
    attachments = RFQAttachmentSerializer(many=True, read_only=True)
    equipment_categories = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentCategory.objects.all(), many=True
    )
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RFQ
        fields = [
            'id',
            'created_by',
            'title',
            'description',
            'pickup_location',
            'rental_start_date',
            'rental_end_date',
            'equipment_categories',
            'notes_per_category',
            'expiry_date',
            'status',
            'visibility',
            'created_at',
            'attachments',
        ] 