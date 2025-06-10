from rest_framework import serializers

from user.models import AdditionalPhoneNumber
from user.models import AdditionalEmail

class AdditionalPhoneNumberSerializer(serializers.ModelSerializer):
    """Serializer for the organization object."""

    class Meta:
        model = AdditionalPhoneNumber
        fields = (
            "id", "phone_number", "confirmation", "rental_notification",
            "buy_and_sell_notification", "pro_notification",
            "user"
        )

        read_only_fields = ("id", "user")


class AdditionalEmailSerializer(serializers.ModelSerializer):
    """Serializer for the organization object."""

    class Meta:
        model = AdditionalEmail
        fields = (
            "id", "email", "confirmation", "rental_notification",
            "buy_and_sell_notification", "pro_notification",
            "user"
        )

        read_only_fields = ("id", "user")


class AdditionalInfoSerializer(serializers.Serializer):
    """Single Serializer for Both Info"""

    additional_email = AdditionalEmailSerializer(many=True, read_only=True)
    additional_phone_number = AdditionalPhoneNumberSerializer(many=True, read_only=True)

