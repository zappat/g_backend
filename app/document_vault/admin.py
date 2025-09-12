from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'file', 'uploaded_at']
    list_filter = ['uploaded_at', 'user']
    search_fields = ['name', 'user__email']
    readonly_fields = ['uploaded_at']