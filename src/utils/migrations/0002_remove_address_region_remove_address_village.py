# Generated by Django 5.0.6 on 2024-07-17 13:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='region',
        ),
        migrations.RemoveField(
            model_name='address',
            name='village',
        ),
    ]
