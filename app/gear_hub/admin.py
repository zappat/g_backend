from django.contrib import admin
from .models import GearCategories, GearItem, GearItemPicture, Booking, AddFavorite, Review, GearItemRent, Cart


admin.site.register(GearCategories)
admin.site.register(GearItem)
admin.site.register(GearItemPicture)
admin.site.register(Booking)
admin.site.register(AddFavorite)
admin.site.register(Review)
admin.site.register(GearItemRent)   
admin.site.register(Cart)