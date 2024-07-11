from django.db import models
from django.utils.translation import gettext as _


class CreatedUpdatedMixin(models.Model):
    updated_at = models.DateTimeField(
        verbose_name=_('last update'),
        auto_now=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Address(CreatedUpdatedMixin):
    region = models.CharField(
        verbose_name=_('oblast'),
        max_length=100,
    )
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
    village = models.CharField(
        verbose_name=_('village'),
        max_length=100,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    def __str__(self):
        values = [
            getattr(self, attr) for attr in ('region', 'city', 'village', 'street', 'number') if getattr(self, attr)
        ]
        return f"Address({', '.join(values)})"
