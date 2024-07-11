"""
Rest Framework Settings
Docs: https://www.django-rest-framework.org/
"""

from core.settings.components.base import INSTALLED_APPS

INSTALLED_APPS += [
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'EXCEPTION_HANDLER': 'drf_standardized_errors.handler.exception_handler',
}
