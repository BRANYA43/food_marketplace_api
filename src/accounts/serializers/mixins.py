from django.contrib.auth.password_validation import validate_password
from django.db.migrations import serializer

from accounts.services import normalizers
from accounts import validators


class PasswordValidationMixin(serializer.Serializer):
    """Serializer Mixin to validate a password"""

    def validate_password(self, value: str):
        validate_password(value, self.instance)  # type: ignore
        return value


class PhoneNumberValidationMixin(serializer.Serializer):
    """Serializer Mixin to validate a phone number"""

    def validate_phone(self, value: str):
        validators.UkrainianPhoneNumberValidator()(value)
        value = normalizers.UkrainianPhoneNumberNormalizer()(value)
        return value
