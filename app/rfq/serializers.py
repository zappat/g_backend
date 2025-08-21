from rest_framework import serializers
from .models import RFQ, RFQAttachment
from user.models import EquipmentCategory
import json
import mimetypes
from datetime import timezone

class RFQAttachmentSerializer(serializers.ModelSerializer):
    file_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RFQAttachment
        fields = ['id', 'rfq', 'file', 'uploaded_at', 'file_info']

    def get_file_info(self, obj):
        # Determine name and size
        file_name = obj.file.name.split('/')[-1] if obj.file and obj.file.name else None
        try:
            file_size = obj.file.size if obj.file else None
        except Exception:
            file_size = None

        # Determine content type
        guessed_type, _ = mimetypes.guess_type(file_name or '')
        content_type = guessed_type or ''

        # Determine last modified - prefer storage modified time, fallback to uploaded_at
        try:
            storage_modified_dt = obj.file.storage.get_modified_time(obj.file.name)
        except Exception:
            storage_modified_dt = None

        dt = storage_modified_dt or obj.uploaded_at
        try:
            # Ensure aware datetime for timestamp conversion
            if dt and dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            last_modified_ms = int(dt.timestamp() * 1000) if dt else None
            last_modified_str = dt.isoformat() if dt else None
        except Exception:
            last_modified_ms = None
            last_modified_str = None

        return {
            'lastModified': last_modified_ms,
            'lastModifiedDate': last_modified_str,
            'name': file_name,
            'size': file_size,
            'type': content_type,
            'webkitRelativePath': ''
        }

class RFQSerializer(serializers.ModelSerializer):
    attachments = RFQAttachmentSerializer(many=True, read_only=True)
    equipment_categories = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentCategory.objects.all(), many=True, required=False
    )
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = RFQ
        fields = [
            'id',
            'created_by',
            'title',
            'description',
            'pickup_location',
            'rental_start_date',
            'rental_end_date',
            'equipment_categories',
            'notes_per_category',
            'expiry_date',
            'status',
            'visibility',
            'created_at',
            'attachments',
            'saved',
            'views',
        ]

    def to_internal_value(self, data):
        # Handle QueryDict data where each field is a list
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, list) and len(value) == 1:
                processed_data[key] = value[0]
            else:
                processed_data[key] = value

        print("processed_data", processed_data)
        
        # Handle equipment_categories - can be IDs, names, or comma-separated strings
        if 'equipment_categories' in processed_data:
            equipment_categories_data = processed_data['equipment_categories']
            
            if isinstance(equipment_categories_data, str):
                # Handle comma-separated string
                if not equipment_categories_data.strip():
                    processed_data = processed_data.copy()
                    processed_data['equipment_categories'] = []
                else:
                    category_ids = []
                    for item in equipment_categories_data.split(','):
                        item = item.strip()
                        if item:
                            try:
                                # Try to convert to integer (ID)
                                category_ids.append(int(item))
                            except ValueError:
                                # If not an integer, treat as category name
                                try:
                                    # Try exact match first
                                    category = EquipmentCategory.objects.get(name__iexact=item)
                                    category_ids.append(category.id)
                                except EquipmentCategory.DoesNotExist:
                                    # Try singular/plural variations
                                    singular = item.rstrip('s') if item.endswith('s') else item
                                    plural = item + 's' if not item.endswith('s') else item
                                    
                                    try:
                                        category = EquipmentCategory.objects.get(name__iexact=singular)
                                        category_ids.append(category.id)
                                    except EquipmentCategory.DoesNotExist:
                                        try:
                                            category = EquipmentCategory.objects.get(name__iexact=plural)
                                            category_ids.append(category.id)
                                        except EquipmentCategory.DoesNotExist:
                                            # Skip invalid categories instead of failing
                                            continue
                    
                    processed_data = processed_data.copy()
                    processed_data['equipment_categories'] = category_ids
            
            elif isinstance(equipment_categories_data, list):
                # Handle list of items (could be IDs or names)
                category_ids = []
                for item in equipment_categories_data:
                    if isinstance(item, int):
                        category_ids.append(item)
                    elif isinstance(item, str):
                        try:
                            # Try to convert to integer (ID)
                            category_ids.append(int(item))
                        except ValueError:
                            # If not an integer, treat as category name
                            try:
                                # Try exact match first
                                category = EquipmentCategory.objects.get(name__iexact=item)
                                category_ids.append(category.id)
                            except EquipmentCategory.DoesNotExist:
                                # Try singular/plural variations
                                singular = item.rstrip('s') if item.endswith('s') else item
                                plural = item + 's' if not item.endswith('s') else item
                                
                                try:
                                    category = EquipmentCategory.objects.get(name__iexact=singular)
                                    category_ids.append(category.id)
                                except EquipmentCategory.DoesNotExist:
                                    try:
                                        category = EquipmentCategory.objects.get(name__iexact=plural)
                                        category_ids.append(category.id)
                                    except EquipmentCategory.DoesNotExist:
                                        # Skip invalid categories instead of failing
                                        continue
                
                processed_data = processed_data.copy()
                processed_data['equipment_categories'] = category_ids
        
        # Handle expiry_date - if empty string, set to None (will be handled by model validation)
        if 'expiry_date' in processed_data and processed_data['expiry_date'] == '':
            processed_data = processed_data.copy()
            processed_data['expiry_date'] = None
        
        # Handle notes_per_category - it's a TextField, not JSONField
        if 'notes_per_category' in processed_data:
            if isinstance(processed_data['notes_per_category'], str) and not processed_data['notes_per_category'].strip():
                processed_data = processed_data.copy()
                processed_data['notes_per_category'] = ''
        
        return super().to_internal_value(processed_data) 