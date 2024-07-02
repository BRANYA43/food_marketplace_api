from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _


def _get_default_grades() -> dict:
    return {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}


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
    slug = models.CharField(
        verbose_name=_('slug'),
        max_length=50,
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
        return str(self.slug)


class Advert(CreatedUpdatedMixin):
    user = models.ForeignKey(
        verbose_name=_('user'),
        to=get_user_model(),
        on_delete=models.PROTECT,
    )
    category = models.ForeignKey(
        verbose_name=_('category'),
        to=Category,
        on_delete=models.PROTECT,
    )
    title = models.CharField(
        verbose_name=_('title'),
        max_length=100,
        unique_for_date='created_at',
    )
    price = models.DecimalField(
        verbose_name=_('price'),
        max_digits=12,
        decimal_places=2,
    )
    descr = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )
    address = models.CharField(
        verbose_name=_('address'),
        max_length=256,
    )
    grades = models.JSONField(
        verbose_name=_('grades'),
        default=_get_default_grades,
    )
    is_displayed = models.BooleanField(
        verbose_name=_('displayed'),
        default=True,
    )

    class Meta:
        verbose_name = _('advert')
        verbose_name_plural = _('adverts')
        ordering = ('is_displayed', 'created_at')
        constraints = (
            models.CheckConstraint(
                name='price_gte_0',
                check=Q(price__gte=0),
            ),
        )

    def __str__(self):
        return self.title

    @property
    def grade(self) -> int | float:
        totals = [int(grade) * count for grade, count in self.grades.items()]
        return round(sum(totals) / 5)


class AdvertImage(CreatedUpdatedMixin):
    advert = models.ForeignKey(
        verbose_name=_('advert'),
        to=Advert,
        on_delete=models.CASCADE,
        related_name='image_set',
    )
    origin = models.ImageField(
        verbose_name=_('origin'),
        upload_to='images/adverts/',
    )
    order_num = models.PositiveIntegerField(
        verbose_name=_('order'),
        help_text=_('Image with order value as 0 will be cover image. Other images will be extra images.'),
    )

    class Meta:
        verbose_name = _('advert image')
        verbose_name_plural = _('advert images')
        ordering = ('advert', 'order_num')
        constraints = (
            models.UniqueConstraint(
                fields=('advert', 'order_num'),
                name='unique_advert_and_order_num',
            ),
        )

    def __str__(self):
        return f'Image[{self.order_num}] of {self.advert.title}'
