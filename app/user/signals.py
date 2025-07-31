from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth import get_user_model
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail, EmailMessage
from django.db.models.signals import post_delete, post_save

from user.models import IdentityVerification, MerchantProfile, RenterProfile

User = get_user_model()

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    """
    email_plaintext_message = f"Open the link to reset your password: https://gearconnect-web.vercel.app/new-password/?token={reset_password_token.key}"

    # Assuming you have a function to send email
    send_mail(
        # title:
        "Password Reset for {title}".format(title="Your Website Title"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@yourdomain.com",
        # to:
        [reset_password_token.user.email]
    )
    
@receiver(post_delete, sender=IdentityVerification)
def delete_identity_document_from_s3(sender, instance, **kwargs):
    """
    Deletes the document file from S3 storage when the corresponding `IdentityVerification` object is deleted.
    """
    if instance.document:
        instance.document.delete(save=False)

@receiver(post_delete, sender=MerchantProfile)
def delete_merchant_profile_pictures_from_s3(sender, instance, **kwargs):
    """
    Deletes the profile and cover pictures from S3 storage when the corresponding `MerchantProfile` object is deleted.
    """
    if instance.profile_picture and instance.profile_picture.name != 'profile-photo/default.png':
        instance.profile_picture.delete(save=False)
    if instance.cover_picture and instance.cover_picture.name != 'cover-photo/default.png':
        instance.cover_picture.delete(save=False)

@receiver(post_delete, sender=RenterProfile)
def delete_renter_profile_pictures_from_s3(sender, instance, **kwargs):
    """
    Deletes the profile and cover pictures from S3 storage when the corresponding `RenterProfile` object is deleted.
    """
    if instance.profile_picture and instance.profile_picture.name != 'profile-photo/default.png':
        instance.profile_picture.delete(save=False)
    if instance.cover_picture and instance.cover_picture.name != 'cover-photo/default.png':
        instance.cover_picture.delete(save=False)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Creates a profile instance based on user role"""
    if created:
        if instance.role == 'merchant':
            MerchantProfile.objects.create(user=instance)
        elif instance.role == 'renter':
            RenterProfile.objects.create(user=instance)