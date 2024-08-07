from django.db.models.signals import post_delete
from django.dispatch import receiver

from catalogs.models.models import Advert


@receiver(post_delete, sender=Advert)
def delete_advert_address(sender, instance, **kwargs):
    if (address := instance.address.first()) is not None:
        address.delete()
