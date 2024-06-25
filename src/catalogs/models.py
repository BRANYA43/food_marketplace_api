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


class Category(CreatedUpdatedMixin):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
        db_index=True,
    )
    parent = models.ForeignKey(
        verbose_name=_('parent category'),
        to='self',
        on_delete=models.PROTECT,
        related_name='children',
        null=True,
        blank=True,
    )
    is_displayed = models.BooleanField(
        verbose_name=_('displayed'),
        default=True,
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ('parent__name', 'name')

    def __str__(self):
        return self.name
