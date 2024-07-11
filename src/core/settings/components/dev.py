"""
Development settings
"""

from core.settings import env
from core.settings.components import BASE_DIR
from core.settings.components.base import INSTALLED_APPS

DEBUG = True

INSTALLED_APPS += [
    'django_extensions',
]

if env.get('DOCKER_RUN', '').lower() in ('true', '1'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': env.get('POSTGRES_HOST'),
            'PORT': env.get('POSTGRES_PORT', '5432'),
            'NAME': env.get('POSTGRES_DB'),
            'USER': env.get('POSTGRES_USER'),
            'PASSWORD': env.get('POSTGRES_PASSWORD'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / '../db.sqlite3'),
        }
    }
