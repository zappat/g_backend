from rest_framework import generics, permissions, exceptions

from gear_hub.serializers import GearCategoriesSerializers
from gear_hub.models import GearCategories


class GearCategoriesListAPIView(generics.ListAPIView):
    """Return list of gear categories"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = GearCategoriesSerializers

    def get_queryset(self):
        category_id = self.request.query_params.get('category_id')

        if category_id:
            try:
                return GearCategories.objects.filter(id=category_id)
            except GearCategories.DoesNotExist:
                raise exceptions.ValidationError("Category with the provided ID does not exist.")
        else:
            return GearCategories.objects.all()
