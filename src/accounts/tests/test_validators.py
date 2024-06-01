from unittest import TestCase

from rest_framework.exceptions import ValidationError

from accounts import validators


class UkrainianPhoneValidatorsTest(TestCase):
    def setUp(self) -> None:
        self.validator_fn = validators.validate_ukrainian_phone

    def test_validator_doesnt_raise_error_for_valid_phones(self):
        valid_phones = [
            '+38 (123) 456 78 90',
            '+38 (123) 456 78-90',
            '+38 (123) 45678 90',
            '+38 (123) 45678-90',
            '+38 (123) 45 67 890',
            '+38 (123) 45-67 890',
            '+38 (123) 45 67890',
            '+38 (123) 45-67890',
            '+38 123 456 78 90',
            '+38 123 456 78-90',
            '+38 123 45678 90',
            '+38 123 45678-90',
            '+38 123 45 67 890',
            '+38 123 45-67 890',
            '+38 123 45 67890',
            '+38 123 45-67890',
            '(123) 456 78 90',
            '(123) 456 78-90',
            '(123) 45678 90',
            '(123) 45678-90',
            '(123) 45 67 890',
            '(123) 45-67 890',
            '(123) 45 67890',
            '(123) 45-67890',
            '123 456 78 90',
            '123 456 78-90',
            '123 45678 90',
            '123 45678-90',
            '123 45 67 890',
            '123 45-67 890',
            '123 45 67890',
            '123 45-67890',
            '1234567890',
            '+381234567890',
            '+38(123)4567890',
            '(123)4567890',
        ]
        for phone in valid_phones:
            self.validator_fn(phone)  # not raise

    def test_validator_raise_error_for_invalid_phone(self):
        invalid_phones = [
            '+38 1234 567 890',
            '+38 (12) 345 67890',
            '+38 (1234) 567 890',
            '123 45 6789',
            '(12) 345 67890',
            '1234 567 890',
            '+38 1234 56 7890',
            '(1234) 567 890',
            '+38 123 45 6789',
        ]

        for phone in invalid_phones:
            self.assertRaisesRegex(
                ValidationError,
                r'Phone must be at ukrainian format\. Example \+38 XXX XXX XXXX\.',
                self.validator_fn,
                phone,
            )
