from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import User
from core.mixins import UUIDBase
from user.utils import get_gear_items_picture_path
from user.models import MerchantProfile
from app.storage_backends import PublicMediaStorage


def default_JSON():
    return []

class GearCategories(UUIDBase):
    """Model for gear categories."""
    category_name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    def save(self, *args, **kwargs):
        # Check if the current category already has a parent
        if self.parent:
            # Check if the parent of the current category already has a parent
            if self.parent.parent:
                # Check if the parent of the parent of the current category already has a parent
                if self.parent.parent.parent:
                    raise ValidationError(
                        _('A category cannot have more than three levels of hierarchy.'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}-{self.category_name}"

    def get_all_category_ids(self):
        """
        Recursively get all the child category ids for this category.
        """
        category_ids = [self.id]
        children = self.children.all()

        for child in children:
            category_ids.extend(child.get_all_category_ids())
        return category_ids

    @classmethod
    def filter_by_category(cls, queryset, category_id):
        """
        Filter gear items by category, including all child categories.
        """
        try:
            category = cls.objects.get(id=category_id)
        except (ValueError, cls.DoesNotExist):
            return queryset.none()

        category_ids = category.get_all_category_ids()
        return queryset.filter(category__id__in=category_ids)


class GearItem(UUIDBase):
    """Model for gear item listing."""

    class LocatiionPrivacy(models.TextChoices):
        PUBLIC = ('public', _('Public'))
        PRIVATE = ('private', _('Private'))
        CLOSED = ('closed', _('Closed'))
        DRAFT = ('draft', _('Draft'))
        PACKAGING_ONLY = ('packaging_only', _('Packaging Only'))

    created_by = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, null=True, blank=True)
    equipment_name = models.CharField(max_length=100)
    key_specifications = models.TextField()
    additional_notes = models.TextField(blank=True, null=True)
    equipment_category = models.ForeignKey(GearCategories, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    description = models.TextField()
    rent_start_date = models.DateField(blank=True, null=True)
    rent_end_date = models.DateField(blank=True, null=True)
    pick_up_location = models.JSONField(default=default_JSON)
    brand = models.CharField(max_length=200, blank=True, null=True)
    model = models.CharField(max_length=200, blank=True, null=True)
    replacement_value = models.IntegerField(blank=True, null=True)
    location_privacy = models.CharField(
        max_length=20, choices=LocatiionPrivacy.choices , 
        default=LocatiionPrivacy.PUBLIC)
    status = models.CharField(max_length=100, blank=True, null=True)
    visibility = models.CharField(max_length=100, blank=True, null=True)
    promotion = models.CharField(max_length=100, blank=True, null=True)
    total_views = models.IntegerField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
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

class GearItemRent(UUIDBase):
    """Model for gear items rent."""

    details = models.TextField()
    included_accessories = models.JSONField(default=default_JSON) 
    daily_rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.IntegerField()
    qty_rented = models.IntegerField(default=0)
    blocked_dates = models.JSONField(default=default_JSON)
    gear_item = models.ForeignKey(GearItem, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.gear_item.name} - {self.gear_item.id}"
    
    
class Review(UUIDBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gear_item = models.ForeignKey(GearItem, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()

    def __str__(self):
        return f"{self.user.email} - {self.gear_item.name }"
    


class Cart(UUIDBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gear_item = models.ForeignKey(GearItem, on_delete=models.CASCADE)
    pick_up_date = models.DateField(null=True, blank=True)
    drop_off_date = models.DateField(null=True, blank=True)
    has_booked = models.BooleanField(default=False)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_days = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id} - {self.gear_item.id}"

class Booking(UUIDBase):
    """Model for gear items bookings."""

    class BookingStatus(models.TextChoices):
        AWAITING_CONFIRMATION = ('awaiting_confirmation', _('Awaiting Confirmation'))
        ACCEPTED = ('accepted', _('Accepted'))
        REJECTED = ('rejected', _('Rejected'))
        PAID = ('paid', _('Paid'))

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=30, choices=BookingStatus.choices, default=BookingStatus.AWAITING_CONFIRMATION
    )

