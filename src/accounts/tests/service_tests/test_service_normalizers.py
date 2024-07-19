from unittest import TestCase

from accounts.services import normalizers


class UkrainianPhoneNumberNormalizerTest(TestCase):
    normalizer = normalizers.UkrainianPhoneNumberNormalizer()

    def test_normalizer_returns_phone_number_expected_format(self):
        expected_phone = '+38 (012) 345 6789'
        raw_phones = [
            '+38(012)3456789',
            '+380123456789',
            '38 012 345 6789',
            '(012) 345 6789',
            '(012)3456789',
            '0123456789',
        ]
        for raw_phone in raw_phones:
            phone = self.normalizer(raw_phone)
            self.assertEqual(phone, expected_phone)

    def test_normalizer_doesnt_normalize_invalid_phone(self):
        invalid_phones = [
            # less at 1 number
            '+38 (012) 345 678',
            '38 012 345 678',
            '(012) 345 678',
            '012 345 678',
            '+38(012)345678',
            '38012345678',
            '(012)345678',
            '012345678',
            # more at 1 number
            '+38 (012) 345 67890',
            '38 012 345 67890',
            '(012) 345 67890',
            '012 345 67890',
            '+38(012)34567890',
            '3801234567890',
            '(012)34567890',
            '01234567890',
            # another country code
            '+10 (012) 345 6789',
            '10 012 345 6789',
            '+10(012)3456789',
            '100123456789',
        ]
        for invalid_phone in invalid_phones:
            phone = self.normalizer(invalid_phone)
            self.assertEqual(phone, invalid_phone)
