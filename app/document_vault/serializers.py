from rest_framework import serializers
from .models import Document
import mimetypes
from datetime import timezone


class DocumentSerializer(serializers.ModelSerializer):
    file_info = serializers.SerializerMethodField(read_only=True)
    file_size = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()
    
    class Meta:
        model = Document
        fields = [
            'id',
            'name',
            'file',
            'uploaded_at',
            'file_info',
            'file_size',
            'file_extension'
        ]
        read_only_fields = ['id', 'uploaded_at', 'file_size', 'file_extension']
    
    def get_file_info(self, obj):
        """Return file information similar to RFQAttachmentSerializer"""
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
    
    def create(self, validated_data):
        """Override create to set the user automatically"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)