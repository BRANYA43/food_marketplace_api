from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext as _

from utils.models.mixins import CreatedUpdatedMixin
from utils.models import Address

User = get_user_model()


class Image(CreatedUpdatedMixin):
    class Type(models.IntegerChoices):
        MAIN = 0, _('main')
        EXTRA = 1, _('extra')

    advert = models.ForeignKey(
        verbose_name=_('advert'),
        to='Advert',
        on_delete=models.CASCADE,
        related_name='images',
    )
    file = models.ImageField(
        verbose_name=_('file'),
        upload_to='images/%Y/%m/%d',
    )
    type = models.PositiveIntegerField(
        verbose_name=_('type'),
        choices=Type.choices,
    )

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')

    def __str__(self):
        return f'{self.advert.name} {self.type} image'


class Advert(CreatedUpdatedMixin):
    owner = models.ForeignKey(
        verbose_name=_('owner'),
        to=User,
        on_delete=models.PROTECT,
        related_name='adverts',
    )
    category = models.ForeignKey(
        verbose_name=_('category'),
        to='Category',
        on_delete=models.PROTECT,
        related_name='adverts',
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=70,
    )
    descr = models.CharField(
        verbose_name=_('description'),
        max_length=1024,
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        verbose_name=_('price'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_('quantity'),
        default=1,
        validators=[MinValueValidator(1)],
    )
    pickup = models.BooleanField(
        verbose_name=_('pickup'),
        default=False,
    )
    nova_post = models.BooleanField(
        verbose_name=_('nova_post'),
        default=False,
    )
    courier = models.BooleanField(
        verbose_name=_('courier'),
        default=True,
    )
    address = GenericRelation(
        verbose_name=_('pickup address'),
        to=Address,
    )

    class Meta:
        verbose_name = _('advert')
        verbose_name_plural = _('adverts')

    def clean_pickup_nova_post_courier(self):
        if not any([self.pickup, self.nova_post, self.pickup]):
            raise ValidationError(
                'One of the fields "pickup", "nova_post", "courier" must be True.',
                'invalid_select',
            )

    def clean_pickup_address_and_pickup(self):
        if self.pickup and not self.address.first():
            raise ValidationError(
                'The "pickup_address" field must be if "pickup" field is True.',
                'invalid_pickup_address',
            )

    def clean(self):
        self.clean_pickup_nova_post_courier()
        self.clean_pickup_address_and_pickup()

    def __str__(self):
        return self.name


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
