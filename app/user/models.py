from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

from core.mixins import UUIDBase
from core.models import User

from user.utils import (get_upload_path, profile_picture_path, cover_picture_path)
from app.storage_backends import PublicMediaStorage, PrivateMediaStorage

class IdentityVerification(UUIDBase):
    """Model for user identity verification."""

    class DocumentsType(models.TextChoices):

        PASSPORT = ('passport', _('Passport'))
        DRIVER_LICENSE = ('driver_license', _('Driver License'))
        IDENTITY_CARD = ('identity_card', _('Identity Card'))

    document = models.FileField(upload_to=get_upload_path, storage=PrivateMediaStorage)
    document_type = models.CharField(
        max_length=14, choices=DocumentsType.choices
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class MerchantProfile(UUIDBase):
    """Model for merchant user profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='profile-photo/default.png', upload_to=profile_picture_path)
    cover_picture = models.ImageField(default='cover-photo/default.png', upload_to=cover_picture_path)
    # profile_picture = models.ImageField(default='profile-photo/default.png',
    #                                     upload_to=profile_picture_path,
    #                                     storage=PublicMediaStorage)
    # cover_picture = models.ImageField(default='cover-photo/default.png',
    #                                   upload_to=cover_picture_path,
    #                                   storage=PublicMediaStorage)
    display_name = models.CharField(max_length=100)
    contact_email = models.EmailField(max_length=255, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    equipment_categories = models.CharField(max_length=255, blank=True)
    is_pro = models.BooleanField(default=False)
    pro_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk} - {self.user.email}"

    def activate_pro(self, months=1):
        self.is_pro = True
        if self.pro_expires_at  and self.pro_expires_at > timezone.now():
            self.pro_expires_at += timedelta(days=30 * months)
        else:
            self.pro_expires_at = timezone.now() + timedelta(days=30 * months)
        self.save()

    def check_pro_status(self):
        if self.pro_expires_at and self.pro_expires_at < timezone.now():
            self.is_pro = False
            self.save()

class EquipmentCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class RenterProfile(UUIDBase):
    """Model for renter user profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='profile-photo/default.png', upload_to=profile_picture_path)
    cover_picture = models.ImageField(default='cover-photo/default.png', upload_to=cover_picture_path)
    display_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    vimeo_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk} - {self.user.email}"

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
