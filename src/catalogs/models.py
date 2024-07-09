from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from utils.models import CreatedUpdatedMixin, Address


def _get_default_grades() -> dict:
    return {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}


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

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ('parent__name', 'name')

    def __str__(self):
        return str(self.name)


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
    grades = models.JSONField(
        verbose_name=_('grades'),
        default=_get_default_grades,
    )
    use_pickup = models.BooleanField(
        verbose_name=_('pickup'),
        default=False,
    )
    use_nova_post = models.BooleanField(
        verbose_name=_('nova post'),
        default=False,
    )
    use_courier = models.BooleanField(
        verbose_name=_('courier'),
        default=True,
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

    def clean(self):
        if not any([self.use_pickup, self.use_nova_post, self.use_courier]):
            raise ValidationError(
                _('One of next field must be true: use_pickup, use_nova_post, use_courier.'),
                'invalid_use_fields',
            )
        if self.use_pickup and getattr(self, 'address', None) is None:
            raise ValidationError(
                _('Address must be specified if use_pickup field is true.'),
                'empty_address',
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


class AdvertAddress(Address):
    advert = models.OneToOneField(
        verbose_name=_('advert'),
        to=Advert,
        on_delete=models.CASCADE,
        related_name='address',
    )

    class Meta:
        verbose_name = _('advert address')
        verbose_name_plural = _('advert addresses')
        ordering = ('advert',)

    def __str__(self):
        return str(self.advert)
