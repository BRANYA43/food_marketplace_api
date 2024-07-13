from unittest import TestCase

from rest_framework.exceptions import ValidationError

from accounts import validators


class UkrainianPhoneNumberValidatorTest(TestCase):
    validator = validators.UkrainianPhoneNumberValidator()

    def test_validator_doesnt_raise_for_valid_phone(self):
        valid_phones = [
            '+38(012)3456789',
            '+380123456789',
            '38 012 345 6789',
            '(012) 345 6789',
            '(012)3456789',
            '0123456789',
        ]
        for phone in valid_phones:
            self.validator(phone)  # not raise

    def test_validator_raises_for_less_at_10_digits(self):
        invalid_phones = [
            '(012) 345 678',
            '012 345 678',
            '(012)345678',
            '012345678',
        ]
        for phone in invalid_phones:
            with self.assertRaisesRegex(ValidationError, r'invalid_digit_count'):
                self.validator(phone)

    def test_validator_raises_for_more_at_10_digits(self):
        invalid_phones = [
            '(012) 345 67890',
            '012 345 67890',
            '(012)34567890',
            '01234567890',
        ]
        for phone in invalid_phones:
            with self.assertRaisesRegex(ValidationError, r'invalid_digit_count'):
                self.validator(phone)

    def test_validator_raises_for_less_at_12_digits(self):
        invalid_phones = [
            '+38 (012) 345 678',
            '38 012 345 678',
            '+38(012)345678',
            '38012345678',
        ]
        for phone in invalid_phones:
            with self.assertRaisesRegex(ValidationError, r'invalid_digit_count'):
                self.validator(phone)

    def test_validator_raises_for_more_at_12_digits(self):
        invalid_phones = [
            '+38 (012) 345 67890',
            '38 012 345 67890',
            '+38(012)34567890',
            '3801234567890',
        ]
        for phone in invalid_phones:
            with self.assertRaisesRegex(ValidationError, r'invalid_digit_count'):
                self.validator(phone)

    def test_validator_raises_for_non_ukrainian_country_code(self):
        invalid_phone = '+10 (012) 345 6789'
        with self.assertRaisesRegex(ValidationError, r'invalid_country_code'):
            self.validator(invalid_phone)
