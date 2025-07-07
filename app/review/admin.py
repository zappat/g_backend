from django.contrib import admin
from .models import Review
 
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'renter', 'merchant', 'rfq', 'rating', 'would_work_again', 'created_at')
    search_fields = ('renter__email', 'merchant__email', 'rfq__title', 'text')
    list_filter = ('rating', 'would_work_again', 'created_at') 