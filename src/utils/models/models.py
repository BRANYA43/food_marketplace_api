from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext as _

from utils.models.mixins import CreatedUpdatedMixin


class Address(CreatedUpdatedMixin):
    city = models.CharField(
        verbose_name=_('city'),
        max_length=100,
    )
    street = models.CharField(
        verbose_name=_('street'),
        max_length=100,
    )
    number = models.CharField(
        verbose_name=_('number'),
        max_length=10,
    )
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_obj = GenericForeignKey()

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
