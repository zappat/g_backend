from django.contrib import admin
from .models import GearCategories, GearItem, GearItemPicture, AddFavorite

@admin.register(GearItem)
class GearItemAdmin(admin.ModelAdmin):
    list_display = (
        "equipment_name",
        "equipment_category",
        "is_public",
    )
    search_fields = ("equipment_name",)
    list_filter = ("equipment_category", "is_public")

admin.site.register(GearCategories)
admin.site.register(GearItemPicture)
admin.site.register(AddFavorite)