import uuid
from django.db import models
from utils.models.mixins import CreatedUpdatedMixin
from django.conf import settings


class ShippingMethod(models.TextChoices):
    STANDARD = 'standard', 'Standard'
    EXPRESS = 'express', 'Express'


class Status(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class PaymentMethod(models.TextChoices):
    VISA = 'visa', 'Visa'
    MASTERCARD = 'mastercard', 'Mastercard'
    CASH = 'cash', 'Cash'


class Order(CreatedUpdatedMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    shipping_address = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    shipping_method = models.CharField(max_length=20, choices=ShippingMethod.choices)
    notes = models.TextField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.uuid} - {self.customer}"
