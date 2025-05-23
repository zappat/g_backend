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
    location_lat = filters.NumberFilter(method="filter_by_location")    
    location_lon = filters.NumberFilter(method="filter_by_location")    

    class Meta:
        model = GearItem
        fields = ["category", "pick_up", "drop_off", "location_lat", "location_lon"]

    def filter_by_dates(self, queryset, name, value):
        pick_up  = self.data.get("pick_up")
        drop_off = self.data.get("drop_off")

        if pick_up and drop_off:
            overlapping_bookings = Cart.objects.filter(
                Q(pick_up_date__lt=drop_off) & Q(drop_off_date__gt=pick_up)
            ).values_list("gear_item_id", flat=True)

            queryset = queryset.exclude(id__in=overlapping_bookings)

        return queryset

    def filter_by_location(self, queryset, name, value):
        lat = self.data.get("location_lat")
        lon = self.data.get("location_lon")
        if lat and lon:
            user_location = Point(float(lon), float(lat), srid=4326)

            filtered_queryset = queryset.none()

            for item in queryset:
                if item.pick_up_location:
                    try:
                        if isinstance(item.pick_up_location, list) and len(item.pick_up_location) > 0:
                            item_lat = float(item.pick_up_location[0].get("lat", 0))
                            item_lon = float(item.pick_up_location[0].get("lon", 0))
                        elif isinstance(item.pick_up_location, dict):
                            item_lat = float(item.pick_up_location.get("lat", 0))
                            item_lon = float(item.pick_up_location.get("lon", 0))
                        else:
                            continue  

                        item_location = Point(item_lon, item_lat, srid=4326)
                        distance = item_location.distance(user_location) * 111.32  
                        desired_distance = 2  

                        if distance <= desired_distance:
                            filtered_queryset = filtered_queryset | queryset.filter(id=item.id)

                    except (IndexError, ValueError, TypeError) as e:
                        print(f"Error processing item {item.id}: {e}")
                        continue  

            queryset = filtered_queryset
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