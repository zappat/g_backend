from django.db import models
from django.utils.translation import gettext_lazy as _

from core.mixins import UUIDBase
from core.models import User

from user.utils import (get_upload_path, profile_picture_path, cover_picture_path)
from app.storage_backends import PublicMediaStorage, PrivateMediaStorage

class Organization(UUIDBase):
    """User Organization information"""

    class OrganizationType(models.TextChoices):

        PHOTOGRAPHY_STUDIOS = ('photography_studios', _('Photography Studios'))
        PRODUCTION_COMPANIES = ('production_companies',
                                _('Production Companies'))
        EVENT_PLANNER = ('event_planner', _('Event Planners'))
        MARKETING_AGENCIES = ('marketing_agencies', _('Marketing Agencies'))
        EDUCATIONAL_INSTITUTIONS = (
            'educational_institutions', _('Educational Institutions'))
        FREELANCE_PHOTOGRAPHERS_AND_VIDEOGRAPHERS = (
            'freelance_photographers_and_videographers', _('Freelance Photographers and Videographers'))
        TOURISM_COMPANIES = ('tourism_companies', _('Tourism Companies'))
        REAL_STATE_AGENCIES = ('real_state_agencies',
                               _('Real Estate Agencies'))
        CORPORATE_BUSINESSES = ('corporate_businesses',
                                _('Corporate Businesses'))
        NON_PROFIT_ORGANIZATIONS = (
            'non_profit_organizations', _('Non-Profit Organizations'))

    class OrganizationStrength(models.TextChoices):

        MEMBERS_1_TO_5 = ('1-5', _('1-5 members'))
        MEMBERS_6_TO_10 = ('6-10', _('6-10 members'))
        MEMBERS_11_TO_20 = ('11-20', _('11-20 members'))
        MEMBERS_21_TO_50 = ('21-50', _('21-50 members'))
        MEMBERS_51_TO_100 = ('51-100', _('51-100 members'))
        MEMBERS_101_200 = ('101-200', _('101-200 members'))
        MEMBERS_201_TO_500 = ('201-500', _('201-500 members'))
        MEMBERS_501_PLUS = ('501_plus', _('501+ members'))

    organization_name = models.CharField(max_length=50)
    organization_type = models.CharField(
        max_length=50, choices=OrganizationType.choices)
    organization_strength = models.CharField(
        max_length=50, choices=OrganizationStrength.choices)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


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
    equipment_category = models.ForeignKey('EquipmentCategory', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.pk} - {self.user.email}"

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
    
    
class AdditionalEmail(UUIDBase):
    """Model for additional emails for notifications"""

    email = models.EmailField(max_length=255, blank=True, null=True)  
    confirmation = models.BooleanField(default=False)
    rental_notification = models.BooleanField(default=False)
    buy_and_sell_notification = models.BooleanField(default=False)
    pro_notification = models.BooleanField(default=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="additional_emails",
    )


class AdditionalPhoneNumber(UUIDBase):
    """Model for additional phone numbers for notifications"""

    phone_number = models.CharField(max_length=20, blank=True, null=True)  
    confirmation = models.BooleanField(default=False)
    rental_notification = models.BooleanField(default=False)
    buy_and_sell_notification = models.BooleanField(default=False)
    pro_notification = models.BooleanField(default=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="additional_phone_numbers",
    )
