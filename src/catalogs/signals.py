from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from catalogs import models


@receiver(post_delete, sender=models.AdvertImage)
def reorder_after_delete(sender, instance, **kwargs):
    images = models.AdvertImage.objects.filter(advert=instance.advert).order_by('order_num')
    for i, image in enumerate(images):
        image.order_num = i

    images.bulk_update(images, ['order_num'])


@receiver(pre_save, sender=models.AdvertImage)
def set_image_order(sender, instance, **kwargs):
    if instance.pk is None:
        images = models.AdvertImage.objects.filter(advert=instance.advert).order_by('order_num')
        if instance.order_num is None and not images.exists():
            instance.order_num = 0
        else:
            instance.order_num = images.last().order_num + 1
