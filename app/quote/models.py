from django.db import models
from core.models import User
from rfq.models import RFQ

class Quote(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.TextField()
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quote for RFQ {self.rfq.id}"
    
class QuoteAttachment(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    file = models.FileField(upload_to='quote_attachments/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for Quote {self.quote.id}"