from rest_framework import serializers

from user.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for the organization object."""

    class Meta:
        model = Organization
        fields = '__all__'