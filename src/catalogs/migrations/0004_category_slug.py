# Generated by Django 5.0.6 on 2024-06-28 11:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('catalogs', '0003_advertimage_advertimage_unique_advert_and_order_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.CharField(default='slug', max_length=50, verbose_name='slug'),
            preserve_default=False,
        ),
    ]