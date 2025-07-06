from django.contrib import admin
from .models import GearCategories, GearItem, GearItemPicture, Booking, AddFavorite, Review, GearItemRent, Cart

@admin.register(GearItem)
class GearItemAdmin(admin.ModelAdmin):
    list_display = (
        "equipment_name",
        "equipment_category",
        "owner",
        "is_public",
    )
    search_fields = ("equipment_name",)
    list_filter = ("equipment_category", "is_public")

admin.site.register(GearCategories)
admin.site.register(GearItemPicture)
admin.site.register(Booking)
admin.site.register(AddFavorite)
admin.site.register(Review)
admin.site.register(GearItemRent)   
admin.site.register(Cart)