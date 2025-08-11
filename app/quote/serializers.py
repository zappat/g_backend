from rest_framework import serializers
from .models import Quote


class QuoteSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Quote
        fields = [
            "id",
            "created_by",
            "quote",
            "rfq",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

