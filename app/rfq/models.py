from django.db import models
from core.models import User
from user.models import EquipmentCategory

class RFQ(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Accepted', 'Accepted'),
    ]
    VISIBILITY_CHOICES = [
        ('Public', 'Public'),
        ('Private', 'Private'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    pickup_location = models.CharField(max_length=255)
    rental_start_date = models.DateField()
    rental_end_date = models.DateField()
    equipment_categories = models.ManyToManyField(EquipmentCategory)
    notes_per_category = models.TextField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Open')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='Public')
    created_at = models.DateTimeField(auto_now_add=True)
    saved_by = models.ManyToManyField(User, related_name='saved_rfqs', blank=True)
    reported_by = models.ManyToManyField(User, related_name='reported_rfqs', blank=True)
    views = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"RFQ: {self.title or self.id} by {self.created_by}"

class RFQAttachment(models.Model):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='rfq-attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for RFQ {self.rfq.id}" 