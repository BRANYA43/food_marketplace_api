from django.utils.translation import gettext as _

from catalogs.models.models import Image


class MainImage(Image):
    class Meta:
        verbose_name = _('Main Image')
        verbose_name_plural = _('Main Images')
        proxy = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.type = self.Type.MAIN
        super().save(force_insert, force_update, using, update_fields)
