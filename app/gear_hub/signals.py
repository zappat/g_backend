from django.db.models.signals import post_delete
from django.dispatch import receiver
from gear_hub.models import GearItemPicture

@receiver(post_delete, sender=GearItemPicture)
def delete_file_from_s3(sender, instance, **kwargs):
    """
    Deletes file from S3 storage when the corresponding GearItemPicture object is deleted.
    """
    if instance.image:
        instance.image.delete(save=False)
