from rest_framework import serializers
from gear_hub.models import GearCategories


class GearCategoriesSerializers(serializers.ModelSerializer):
    """Serialize for gear categories."""

    children = serializers.SerializerMethodField()
    class Meta:
        model = GearCategories
        fields = '__all__'

    def get_children(self, obj):
        children  = GearCategories.objects.filter(parent=obj)
        serializer = GearCategoriesSerializers(children, many=True)
        return serializer.data
