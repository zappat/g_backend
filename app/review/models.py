from django.db import models
from core.models import User
from rfq.models import RFQ

class Review(models.Model):
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    would_work_again = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('renter', 'merchant', 'rfq')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.renter.email} for {self.merchant.email} (RFQ {self.rfq.id})" 