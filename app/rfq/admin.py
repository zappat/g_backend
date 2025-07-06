from django.contrib import admin
from .models import RFQ, RFQAttachment

@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'status', 'visibility', 'expiry_date', 'created_at')
    search_fields = ('title', 'description', 'pickup_location')
    list_filter = ('status', 'visibility', 'expiry_date')

@admin.register(RFQAttachment)
class RFQAttachmentAdmin(admin.ModelAdmin):
    list_display = ('rfq', 'file', 'uploaded_at') 