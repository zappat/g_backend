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
        email = self.normalize_email(email)
        role = extra_fields.get('role', 'renter')
        username = f"{email}_{role}"  # Create unique username from email and role
        
        user = self.model(
            email=email, 
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create save and return a new super user."""
        email = self.normalize_email(email)
        username = f"{email}_admin"  # Superuser gets admin suffix
        
        super_user = self.model(
            email=email, 
            username=username,
            **extra_fields
        )
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

    email = models.EmailField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.RENTER)
    username = models.CharField(max_length=255, unique=True, default='')  # Unique identifier for authentication

    objects = UserManager()

    USERNAME_FIELD = 'username'
    
    class Meta:
        unique_together = ('email', 'role')  # Allow same email for different roles
