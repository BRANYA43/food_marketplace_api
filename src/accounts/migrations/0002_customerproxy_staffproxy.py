# Generated by Django 5.0.6 on 2024-07-19 13:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerProxy',
            fields=[],
            options={
                'verbose_name': 'customer',
                'verbose_name_plural': 'customers',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.user',),
        ),
        migrations.CreateModel(
            name='StaffProxy',
            fields=[],
            options={
                'verbose_name': 'staff',
                'verbose_name_plural': 'staffs',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.user',),
        ),
    ]
