from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager for user."""

    def create_user(self, email, password=None, **extra_fields):
        """Create save and return a new user."""
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create save and return a new super user."""
        super_user = self.model(
            email=self.normalize_email(email), **extra_fields)
        super_user.set_password(password)
        super_user.is_active = True
        super_user.is_staff = True
        super_user.is_superuser = True
        super_user.save(using=self._db)
        return super_user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    class UserRole(models.TextChoices):
        RENTER = ('renter', _('Renter'))
        MERCHANT = ('merchant', _('Merchant'))

    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    roles = models.JSONField(default=list)  # Store roles as a list
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.RENTER,
        help_text='Legacy field - use roles instead')

    objects = UserManager()

    USERNAME_FIELD = 'email'
