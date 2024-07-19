"""
Baton Settings
GitHub: https://github.com/otto-torino/django-baton
"""

from core.settings.components.base import INSTALLED_APPS
from django.utils.translation import gettext_lazy as _

INSTALLED_APPS.insert(0, 'baton')
INSTALLED_APPS.append('baton.autodiscover')

BATON = {
    'SITE_HEADER': 'Food Marketplace',
    'SITE_TITLE': 'Food Marketplace',
    'INDEX_TITLE': _('Site Administration'),
    'SUPPORT_HREF': 'https://github.com/otto-torino/django-baton/issues',
    'COPYRIGHT': 'copyright © 2023 <a href="https://www.otto.to.it">Otto srl</a>',  # noqa
    'POWERED_BY': '<a href="https://www.otto.to.it">Otto srl</a>',
    'CONFIRM_UNSAVED_CHANGES': True,
    'SHOW_MULTIPART_UPLOADING': True,
    'ENABLE_IMAGES_PREVIEW': True,
    'CHANGELIST_FILTERS_IN_MODAL': True,
    'CHANGELIST_FILTERS_ALWAYS_OPEN': False,
    'CHANGELIST_FILTERS_FORM': True,
    'MENU_ALWAYS_COLLAPSED': False,
    'MESSAGES_TOASTS': False,
    'GRAVATAR_DEFAULT_IMG': 'retro',
    'GRAVATAR_ENABLED': True,
    'LOGIN_SPLASH': '/static/core/img/login-splash.png',
    'FORCE_THEME': None,
    'MENU': (
        {'type': 'title', 'label': _('For Administration')},
        {'type': 'model', 'label': _('Staffs'), 'name': 'customerproxy', 'app': 'accounts'},
        {'type': 'model', 'label': _('Groups'), 'name': 'group', 'app': 'auth'},
        {'type': 'title', 'label': _('Marketplace')},
        {'type': 'model', 'label': _('Customers'), 'name': 'staffproxy', 'app': 'accounts'},
        {'type': 'model', 'label': _('Categories'), 'name': 'category', 'app': 'catalogs'},
        {'type': 'title', 'label': _('Tokens')},
        {'type': 'model', 'label': _('Token Black List'), 'name': 'blacklistedtoken', 'app': 'token_blacklist'},
        {'type': 'model', 'label': _('Outstanding Tokens'), 'name': 'outstandingtoken', 'app': 'token_blacklist'},
    ),
}
