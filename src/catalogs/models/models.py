from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxLengthValidator, RegexValidator
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

    def clean(self):
        if not self.pk:
            if self.advert.images.filter(type=self.Type.MAIN).exists() and self.type == self.Type.MAIN:
                raise ValidationError(
                    'Advert already has main image.',
                    'image_conflict',
                )


class Advert(CreatedUpdatedMixin):
    class Unit(models.IntegerChoices):
        G = 0, _('g')
        KG = 1, _('kg')
        T = 2, _('t')
        CM3 = 3, _('cm³')
        DM3 = 4, _('dm³')
        M3 = 5, _('m³')
        ML = 6, _('ml')
        L = 7, _('l')

    class Availability(models.IntegerChoices):
        AVAILABLE = 0, _('is available')
        NOT_AVAILABLE = 1, _('is not available')
        ORDER = 2, _('to order')

    class PaymentMethod(models.IntegerChoices):
        CARD = 0, _('on card')
        CASH = 1, _('in cash')

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
    unit = models.PositiveIntegerField(
        verbose_name=_('unit'),
        choices=Unit.choices,
    )
    availability = models.PositiveIntegerField(
        verbose_name=_('availability'),
        choices=Availability.choices,
        default=Availability.AVAILABLE,
    )
    location = models.CharField(
        verbose_name=_('location'),
        max_length=100,
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
    delivery_comment = models.TextField(
        verbose_name=_('delivery comment'),
        null=True,
        blank=True,
        validators=[MaxLengthValidator(512)],
    )
    payment_method = models.PositiveIntegerField(
        verbose_name=_('preferring payment method'),
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
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

    def clean_pickup_nova_post_courier(self):
        if not any([self.pickup, self.nova_post, self.courier]):
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
