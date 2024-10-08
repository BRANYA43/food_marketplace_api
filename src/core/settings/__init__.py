"""
Combining settings for django project
"""

from split_settings.tools import include

from core.settings.components import env

_settings = (
    'components/base.py',
    'components/cors_headers.py',
    'components/rest_framework.py',
    'components/drf_spectacular.py',
    'components/simple_jwt.py',
    'components/drf_standardized_errors.py',
    'components/baton.py',  # not touch
    'components/{}.py'.format(env.get('DJANGO_SETTINGS_ENV', 'prod').lower()),
)

include(*_settings)
