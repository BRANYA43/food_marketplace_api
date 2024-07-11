from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken

from accounts import managers
from utils.models import Address


class UserAddress(Address):
    user = models.OneToOneField(
        verbose_name=_('user'),
        to='User',
        on_delete=models.CASCADE,
        related_name='address',
    )

    class Meta:
        verbose_name = _('user_address')
        verbose_name_plural = (_('user_addresses'),)

    def __str__(self):
        return str(self.user)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name=_('email'),
        unique=True,
    )
    full_name = models.CharField(
        verbose_name=_('full name'), max_length=100, null=True, blank=True, validators=[MinLengthValidator(2)]
    )
    phone = models.CharField(
        verbose_name=_('Phone Number'),
        max_length=20,
        null=True,
        blank=True,
    )
    is_staff = models.BooleanField(
        verbose_name=_('is staff'),
        default=False,
        help_text=_('Make the account as admin.'),
    )
    is_active = models.BooleanField(
        verbose_name=_('is active'),
        default=True,  # TODO Must be False by default. Only after confirmation of email it is True
        help_text=_('Active|Disable the account.'),
    )
    updated_at = models.DateTimeField(
        verbose_name=_('Last Updated Date'),
        auto_now=True,
    )
    joined_at = models.DateTimeField(
        verbose_name=_('Joined Date'),
        auto_now_add=True,
    )

    USERNAME_FIELD = 'email'

    objects = managers.UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-joined_at', 'is_active']
        get_latest_by = 'joined_at'
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    phone__regex=r'^(\+38)\s(\(\d{3}\))\s(\d{3})\s(\d{4})$',
                ),
                name='phone_at_correct_format',
                violation_error_code='invalid_phone',
                violation_error_message=_('User phone must be at one of format: +38 (050) 000 0000.'),
            ),
        ]

    def __str__(self):
        return self.email

    @property
    def refresh_token(self):
        return RefreshToken.for_user(self)

    @property
    def access_token(self):
        return RefreshToken.for_user(self).access_token  # type: ignore
