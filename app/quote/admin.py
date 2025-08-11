from django.contrib import admin
from .models import Quote, QuoteAttachment


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "rfq", "created_by", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("quote",)
    # Use raw_id_fields to avoid dependency on related admin search configuration
    raw_id_fields = ("created_by", "rfq")


@admin.register(QuoteAttachment)
class QuoteAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "quote", "file", "created_at")
    search_fields = ("file",)
    raw_id_fields = ("quote",)

