import json
from uuid import UUID

from django.db.models import Q
from django_filters import rest_framework as filters
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from gear_hub.models import GearItem, Booking, GearCategories, Cart


class GearItemFilter(filters.FilterSet):
    pick_up = filters.DateTimeFilter(method="filter_by_dates")
    drop_off = filters.DateTimeFilter(method="filter_by_dates")
    category = filters.CharFilter(method="filter_by_category")
    lat = filters.NumberFilter(method="filter_by_location")    
    lon = filters.NumberFilter(method="filter_by_location")    

    class Meta:
        model = GearItem
        fields = ["category", "pick_up", "drop_off", "lat", "lon"]

    def filter_by_dates(self, queryset, name, value):
        pick_up  = self.data.get("pick_up")
        drop_off = self.data.get("drop_off")

        if pick_up and drop_off:
            # First check if the item is available for the requested dates
            queryset = queryset.filter(
                Q(rent_start_date__lte=pick_up) & Q(rent_end_date__gte=drop_off)
            )
            
            # Then check for overlapping bookings
            overlapping_bookings = Cart.objects.filter(
                Q(pick_up_date__lt=drop_off) & Q(drop_off_date__gt=pick_up)
            ).values_list("gear_item_id", flat=True)

            queryset = queryset.exclude(id__in=overlapping_bookings)

        return queryset

    def filter_by_location(self, queryset, name, value):
        lat = self.data.get("lat")
        lon = self.data.get("lon")
        
        if lat and lon:
            try:
                user_lat = float(lat)
                user_lon = float(lon)
                filtered_queryset = queryset.none()

                for item in queryset:
                    if item.pick_up_location and isinstance(item.pick_up_location, dict):
                        # Get bounding box from pick_up_location
                        boundingbox = item.pick_up_location.get('boundingbox', [])
                        if len(boundingbox) == 4:
                            min_lat = float(boundingbox[0])
                            max_lat = float(boundingbox[1])
                            min_lon = float(boundingbox[2])
                            max_lon = float(boundingbox[3])
                            
                            # Check if user coordinates are within the bounding box
                            if (min_lat <= user_lat <= max_lat and 
                                min_lon <= user_lon <= max_lon):
                                filtered_queryset = filtered_queryset | queryset.filter(id=item.id)

                queryset = filtered_queryset
            except (ValueError, TypeError) as e:
                print(f"Error processing coordinates: {e}")
                
        return queryset

    def get_all_category_ids(self, category):
        """
        Recursively get all the child category ids for given category 
        """
        category_ids = [category.id]
        children = category.children.all()

        for child in children:
            category_ids.extend(self.get_all_category_ids(child))
        return category_ids
    
    def filter_by_category(self, queryset, name, value):
        """
        Filter gear items by category, including all the child categories.
        """
        category_ids = value.split(",")
        try:
            category_uuid = [UUID(category_id.strip()) for category_id in category_ids]
        except ValueError:
            return queryset
        
        categories = GearCategories.objects.filter(
            Q(id__in=category_uuid) | Q(parent_id__in=category_uuid)
            )

        all_categories = {}
        for category in categories:
            all_categories.setdefault(category.parent_id, []).append(category)

        all_category_ids = set()
        for category in categories:
            all_category_ids.update(self.get_all_category_ids(category))

        if all_category_ids:
            queryset = queryset.filter(category_id__in=all_category_ids)

        return queryset
    
    # def qs(self):
    #     gear_item = 
    #     return super().qs.distinct()