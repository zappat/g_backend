from rest_framework import serializers
from .models import Quote, QuoteAttachment


class QuoteAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteAttachment
        fields = ["id", "quote", "file", "created_at"]


class QuoteCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating quotes with attachments via FormData
    Handles: rfq (string), quote (text), attachments (files)
    """
    rfq = serializers.CharField(write_only=True)  # Frontend sends as string
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Quote
        fields = ["rfq", "quote", "attachments"]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def validate_rfq(self, value):
        """Convert rfq string to integer and validate it exists"""
        try:
            rfq_id = int(value)
            from rfq.models import RFQ
            if not RFQ.objects.filter(id=rfq_id).exists():
                raise serializers.ValidationError("RFQ with this ID does not exist.")
            return rfq_id
        except ValueError:
            raise serializers.ValidationError("RFQ ID must be a valid integer.")

    def create(self, validated_data):
        """Create quote with attachments"""
        attachments = validated_data.pop('attachments', [])
        rfq_id = validated_data.pop('rfq')

        # Get the RFQ instance
        from rfq.models import RFQ
        rfq = RFQ.objects.get(id=rfq_id)

        # Create the quote
        quote = Quote.objects.create(
            rfq=rfq,
            created_by=self.context['request'].user,
            **validated_data
        )

        # Create attachments if provided
        for attachment in attachments:
            QuoteAttachment.objects.create(quote=quote, file=attachment)

        return quote


class QuoteSerializer(serializers.ModelSerializer):
    """Serializer for retrieving quotes with attachments"""
    attachments = QuoteAttachmentSerializer(many=True, read_only=True, source='quoteattachment_set')
    created_by = serializers.IntegerField(source='created_by.id', read_only=True)
    rfq = serializers.IntegerField(source='rfq.id', read_only=True)

    class Meta:
        model = Quote
        fields = [
            "id", "quote", "created_at", "updated_at",
            "created_by", "rfq", "attachments"
        ]