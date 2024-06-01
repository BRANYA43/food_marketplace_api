from datetime import timedelta, datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken


def foo():
    return datetime.now() - timedelta(days=365 * 18)


class User(AbstractBaseUser, PermissionsMixin):
    class Type(models.TextChoices):
        CUSTOMER = 'customer', _('Customer')
        PRODUCER = 'producer', _('Producer')

    email = models.EmailField(
        verbose_name=_('email'),
        unique=True,
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=20,
        choices=Type.choices,
        default=Type.CUSTOMER,
    )
    full_name = models.CharField(
        verbose_name=_('full name'),
        max_length=100,
        null=True,
        blank=True,
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
