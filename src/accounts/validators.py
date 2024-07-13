import re

from django.utils.translation import gettext as _

from rest_framework.exceptions import ValidationError


class UkrainianPhoneNumberValidator:
    def __init__(self):
        self.country_code_pattern = re.compile(r'^\+38')
        self.all_digit_pattern = re.compile(r'\d+')

    def __call__(self, phone: str, *args, **kwargs):
        self.validate_country_code(phone)
        self.validate_digit_count(phone)

    def validate_digit_count(self, phone):
        phone = ''.join(self.all_digit_pattern.findall(phone))
        if len(phone) not in (12, 10):
            raise ValidationError(
                _('Phone number must have 10 digits or 12 digits if number with country code.'),
                'invalid_digit_count',
            )

    def validate_country_code(self, phone: str):
        if phone[0] == '+' and self.country_code_pattern.match(phone) is None:
            raise ValidationError(
                _('Phone number must be ukrainian.'),
                'invalid_country_code',
            )
