# Generated by Django 5.1.1 on 2024-09-10 18:15

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="last update"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="creation"),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("shipped", "Shipped"),
                            ("delivered", "Delivered"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("shipping_address", models.CharField(max_length=255)),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("visa", "Visa"),
                            ("mastercard", "Mastercard"),
                            ("cash", "Cash"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "shipping_method",
                    models.CharField(
                        choices=[("standard", "Standard"), ("express", "Express")],
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                ("is_paid", models.BooleanField(default=False)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
