import re

from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError


def validate_ukrainian_phone(phone: str):
    pattern = re.compile(
        r'^(\+38)?\s?((\(\d{3}\))|(\d{3}))\s?((\d{3}\s?\d{2}(\s|-)?\d{2})|(\d{2}(\s|-)?\d{2}\s?\d{3}))$'
    )

    if pattern.match(phone) is None:
        raise ValidationError(
            _('Phone must be at ukrainian format. Example +38 XXX XXX XXXX.'),
            'invalid_phone',
        )
