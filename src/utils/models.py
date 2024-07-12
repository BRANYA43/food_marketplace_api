from django.db import models
from django.utils.translation import gettext as _


class CreatedUpdatedMixin(models.Model):
    updated_at = models.DateTimeField(
        verbose_name=_('last update'),
        auto_now=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_('creation'),
        auto_now_add=True,
    )

    class Meta:
        abstract = True
