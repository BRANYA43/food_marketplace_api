from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError as rest_ValidationError
from django.core.exceptions import ValidationError as django_ValidationError

from accounts.serializers.mixins import PhoneNumberValidationMixin, PasswordValidationMixin
from utils.tests.cases import SerializerTestCase

User = get_user_model()


class PhoneNumberMixinTest(SerializerTestCase):
    mixin = PhoneNumberValidationMixin

    def test_validate_phone_method_doesnt_raise_and_return_valid_phone(self):
        valid_phone = '+38(012)3456789'
        self.mixin().validate_phone(valid_phone)  # not raises

    def test_validate_phone_method_raises_error_for_invalid_digit_count(self):
        invalid_phones = ['+38(012)345678', '(012)345678']
        for phone in invalid_phones:
            with self.assertRaisesRegex(rest_ValidationError, r'invalid_digit_count'):
                self.mixin().validate_phone(phone)

    def test_validate_phone_method_raises_error_for_invalid_country_code(self):
        invalid_phone = '+10(012)345678'
        with self.assertRaisesRegex(rest_ValidationError, r'invalid_country_code'):
            self.mixin().validate_phone(invalid_phone)


class PasswordValidationMixinTest(SerializerTestCase):
    mixin = PasswordValidationMixin
    mixin.instance = None  # type: ignore

    def test_validate_password_method_doesnt_raise_and_return_valid_password(self):
        valid_password = 'qwe123!@#'
        password = self.mixin().validate_password(valid_password)  # not raise

        self.assertEqual(password, valid_password)

    def test_validate_password_method_raises_error_for_short_password(self):
        short_password = 'qwe123'
        with self.assertRaisesRegex(
            django_ValidationError,
            r'This password is too short. It must contain at least 8 characters.',
        ):
            self.mixin().validate_password(short_password)

    def test_validate_password_method_raises_error_for_numeric_password(self):
        numeric_password = '12345678'
        with self.assertRaisesRegex(
            django_ValidationError,
            r'This password is entirely numeric.',
        ):
            self.mixin().validate_password(numeric_password)
