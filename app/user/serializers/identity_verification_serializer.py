from rest_framework import serializers
from user.models import IdentityVerification

class IdentityVerificationSerializer(serializers.ModelSerializer):
    """serializer for the user identity verification."""

    class Meta:
        model = IdentityVerification
        fields = '__all__'
        
    
    def update(self, instance, validated_data):
        new_document = validated_data.get('document', None)
        if new_document and instance.document:
            instance.document.delete(save=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance