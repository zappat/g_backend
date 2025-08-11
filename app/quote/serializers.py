from rest_framework import serializers
from .models import Quote, QuoteAttachment


class QuoteSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    attachments = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Quote
        fields = [
            "id",
            "created_by",
            "quote",
            "rfq",
            "created_at",
            "updated_at",
            "attachments",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def get_attachments(self, obj):
        qs = QuoteAttachment.objects.filter(quote=obj).order_by("-created_at")
        return QuoteAttachmentSerializer(qs, many=True).data

    def to_internal_value(self, data):
        # Normalize incoming data for common frontend variations
        processed = {}
        for key, value in data.items():
            if isinstance(value, list) and len(value) == 1:
                processed[key] = value[0]
            else:
                processed[key] = value

        # Support rfqId / rfq_id aliases
        if "rfqId" in processed and "rfq" not in processed:
            processed["rfq"] = processed["rfqId"]
        if "rfq_id" in processed and "rfq" not in processed:
            processed["rfq"] = processed["rfq_id"]

        return super().to_internal_value(processed)

class QuoteAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteAttachment
        fields = ["id", "quote", "file", "created_at"]