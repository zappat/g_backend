from rest_framework import serializers
from gear_hub.models import GearCategories


class GearCategoriesSerializers(serializers.ModelSerializer):
    """Serialize for gear categories."""
    class Meta:
        model = GearCategories
        fields = '__all__'
