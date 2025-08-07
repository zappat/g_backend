from rest_framework import serializers
from .models import RFQ, RFQAttachment
from user.models import EquipmentCategory
import json

class RFQAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQAttachment
        fields = ['id', 'rfq', 'file', 'uploaded_at']

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
        
        # Handle status - convert to lowercase to match model choices
        if 'status' in processed_data and isinstance(processed_data['status'], str):
            processed_data = processed_data.copy()
            processed_data['status'] = processed_data['status'].lower()
        
        # Handle visibility - convert to lowercase to match model choices
        if 'visibility' in processed_data and isinstance(processed_data['visibility'], str):
            processed_data = processed_data.copy()
            processed_data['visibility'] = processed_data['visibility'].lower()
        
        # Handle notes_per_category - ensure it's valid JSON
        if 'notes_per_category' in processed_data and isinstance(processed_data['notes_per_category'], str):
            processed_data = processed_data.copy()
            processed_data['notes_per_category'] = processed_data['notes_per_category']
        
        return super().to_internal_value(processed_data) 