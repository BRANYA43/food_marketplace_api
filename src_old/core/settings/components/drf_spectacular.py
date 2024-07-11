from core.settings.components.base import INSTALLED_APPS

INSTALLED_APPS += [
    'drf_spectacular',
]


SPECTACULAR_SETTINGS = {
    'TITLE': 'Food Marketplace API',
    'DESCRIPTION': '',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
