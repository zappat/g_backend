from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import User
from core.mixins import UUIDBase
from user.utils import get_gear_items_picture_path
from app.storage_backends import PublicMediaStorage


def default_JSON():
    return []

class GearCategories(UUIDBase):
    """Model for gear categories."""
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id}-{self.category_name}"


class GearItem(UUIDBase):
    """Model for gear item listing."""

    class LocatiionPrivacy(models.TextChoices):
        PUBLIC = ('public', _('Public'))
        PRIVATE = ('private', _('Private'))
        CLOSED = ('closed', _('Closed'))
        DRAFT = ('draft', _('Draft'))
        PACKAGING_ONLY = ('packaging_only', _('Packaging Only'))

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='created_gear_items')
    equipment_name = models.CharField(max_length=100)
    key_specifications = models.TextField()
    additional_notes = models.TextField(blank=True, null=True)
    equipment_category = models.ForeignKey(GearCategories, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    description = models.TextField()
    pick_up_location = models.JSONField(default=default_JSON)
    location_privacy = models.CharField(
        max_length=20, choices=LocatiionPrivacy.choices , 
        default=LocatiionPrivacy.PUBLIC)
    rentals = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.id}-{self.equipment_name}"


class GearItemPicture(models.Model):
    # image = models.ImageField(upload_to=get_gear_items_picture_path, storage=PublicMediaStorage)
    image = models.ImageField(upload_to=get_gear_items_picture_path)
    is_cover_photo = models.BooleanField(default=False)
    gear_item = models.ForeignKey(GearItem, on_delete=models.CASCADE)


class AddFavorite(UUIDBase):
    """Model for gear items add to favorite."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gear_item = models.ForeignKey(GearItem, on_delete=models.CASCADE)

    def __str__(self):
        return f"Gear Item Id : {self.gear_item.id}"