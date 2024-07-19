from django.db import models
from django.utils.translation import gettext as _

from utils.models import CreatedUpdatedMixin


class Category(CreatedUpdatedMixin):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
    )
    parent = models.ForeignKey(
        verbose_name=_('parent'),
        to='self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return str(self.name)

    @property
    def is_parent(self):
        if self.children.exists():
            return True
        return False

    @property
    def is_child(self):
        if self.parent:
            return True
        return False
