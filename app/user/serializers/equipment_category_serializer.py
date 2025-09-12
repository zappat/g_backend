from rest_framework import serializers
from user.models import EquipmentCategory


class EquipmentCategorySerializer(serializers.ModelSerializer):
    """Serializer for EquipmentCategory model."""
    
    class Meta:
        model = EquipmentCategory
        fields = ['id', 'name'] 