from django.db import models
from core.models import User


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='document-vault/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Document: {self.name or self.file.name} by {self.user}"
    
    @property
    def file_size(self):
        """Return file size in bytes"""
        try:
            return self.file.size if self.file else 0
        except Exception:
            return 0
    
    @property
    def file_extension(self):
        """Return file extension"""
        if self.file and self.file.name:
            return self.file.name.split('.')[-1].lower()
        return None