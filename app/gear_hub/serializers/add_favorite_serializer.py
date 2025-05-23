from rest_framework import serializers
from gear_hub.models import AddFavorite


class AddFavoriteSerializer(serializers.ModelSerializer):
    """Serialize for add favorite gear items."""

    class Meta:
        model = AddFavorite
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}
        
    def create(self, validated_data):
        user = self.context["request"].user
        gear_item = validated_data.get("gear_item")
        if not gear_item:
            raise serializers.ValidationError({"gear_item": "Gear Item id is required"})

        is_favorite = AddFavorite.objects.filter(gear_item=gear_item, user=user)
        if is_favorite:
            raise serializers.ValidationError({"favorite":"Can't mark the same item as favorite again"})
        
        favorite = AddFavorite.objects.create(gear_item=gear_item, user=user)

        return favorite
