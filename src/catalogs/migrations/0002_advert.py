# Generated by Django 5.0.6 on 2024-08-01 16:59
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('catalogs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Advert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='last update')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='creation')),
                ('name', models.CharField(max_length=70, verbose_name='name')),
                ('descr', models.CharField(blank=True, max_length=1024, null=True, verbose_name='description')),
                (
                    'price',
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal('0'))],
                        verbose_name='price',
                    ),
                ),
                (
                    'quantity',
                    models.PositiveIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'
                    ),
                ),
                ('pickup', models.BooleanField(default=False, verbose_name='pickup')),
                ('nova_post', models.BooleanField(default=False, verbose_name='nova_post')),
                ('courier', models.BooleanField(default=True, verbose_name='courier')),
                (
                    'category',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='adverts',
                        to='catalogs.category',
                        verbose_name='category',
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='adverts',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='owner',
                    ),
                ),
            ],
            options={
                'verbose_name': 'advert',
                'verbose_name_plural': 'adverts',
            },
        ),
    ]
