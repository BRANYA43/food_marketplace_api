from django.apps import AppConfig


class CatalogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogs'

    def ready(self):
        from catalogs.models.signals import delete_advert_address  # noqa
