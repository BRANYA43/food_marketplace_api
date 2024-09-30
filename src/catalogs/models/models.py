from functools import partial
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxLengthValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext as _

from utils.models.mixins import CreatedUpdatedMixin

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

    def clean(self):
        if not self.pk:
            if self.advert.images.filter(type=self.Type.MAIN).exists() and self.type == self.Type.MAIN:
                raise ValidationError(
                    'Advert already has main image.',
                    'image_conflict',
                )


class Advert(CreatedUpdatedMixin):
    class DeliveryMethod(models.TextChoices):
        PICKUP = 'pickup', _('pickup')
        NOVA_POST = 'nova_post', _('nova post')
        COURIER = 'courier', _('courier')

    class Unit(models.TextChoices):
        G = 'g', _('g')
        KG = 'kg', _('kg')
        T = 't', _('t')
        CM3 = 'cm3', _('cm³')
        DM3 = 'dm3', _('dm³')
        M3 = 'm3', _('m³')
        ML = 'ml', _('ml')
        L = 'l', _('l')

    class Availability(models.TextChoices):
        AVAILABLE = 'available', _('is available')
        NOT_AVAILABLE = 'not_available', _('is not available')
        ORDER = 'order', _('to order')

    class PaymentMethod(models.TextChoices):
        CARD = 'card', _('on card')
        CASH = 'cash', _('in cash')

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
    unit = models.CharField(
        verbose_name=_('unit'),
        max_length=5,
        choices=Unit.choices,
    )
    availability = models.CharField(
        verbose_name=_('availability'),
        max_length=20,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
    )
    location = models.CharField(
        verbose_name=_('location'),
        max_length=100,
    )
    delivery_methods = ArrayField(
        verbose_name=_('delivery methods'),
        base_field=models.CharField(
            max_length=10,
            choices=DeliveryMethod.choices,
        ),
        size=3,
        default=partial(list, [DeliveryMethod.COURIER]),
    )
    delivery_comment = models.TextField(
        verbose_name=_('delivery comment'),
        null=True,
        blank=True,
        validators=[MaxLengthValidator(512)],
    )
    payment_methods = ArrayField(
        verbose_name=_('preferring payment method'),
        base_field=models.CharField(
            max_length=5,
            choices=PaymentMethod.choices,
        ),
        default=partial(list, [PaymentMethod.CARD]),
        size=2,
    )
    payment_card = models.CharField(
        verbose_name=_('payment card number'),
        max_length=19,
        validators=[
            RegexValidator(
                r'^\d{4} \d{4} \d{4} \d{4}$',
                message=_('Card number should be in the such style: "0000 0000 0000 0000".'),
                code='invalid_card_number',
            ),
        ],
    )
    payment_comment = models.TextField(
        verbose_name=_('payment comment'),
        null=True,
        blank=True,
        validators=[MaxLengthValidator(512)],
    )

    class Meta:
        verbose_name = _('advert')
        verbose_name_plural = _('adverts')

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
