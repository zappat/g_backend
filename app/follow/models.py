from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from core.mixins import UUIDBase


class Follow(UUIDBase):
    """Model for user following relationships."""

    MODE_CHOICES = [
        (1, 'Renter to Merchant'),
        (2, 'Merchant to Renter'),
    ]

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
        help_text='User who is following'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
        help_text='User who is being followed'
    )
    mode = models.IntegerField(
        choices=MODE_CHOICES,
        default=1,
        help_text='1 for renter following merchant, 2 for merchant following renter'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following', 'mode']
        verbose_name = _('Follow')
        verbose_name_plural = _('Follows')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.email} follows {self.following.email}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves.")