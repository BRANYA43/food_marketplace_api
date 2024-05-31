"""
CORS Headers Settings
GitHub: https://github.com/adamchainz/django-cors-headers
"""

from core.settings.components.base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS += ['corsheaders']
MIDDLEWARE += [
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True
