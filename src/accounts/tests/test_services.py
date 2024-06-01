from unittest import TestCase

from accounts import services


class PhoneNormalizerServiceTest(TestCase):
    def setUp(self) -> None:
        self.service_fn = services.normalize_phone_to_ukrainian_format

    def test_service_normalizes_phone_at_expected_format(self):
        expected_phone = '+38 (000) 000 0000'
        raw_phones = [
            '+38 (000) 000 0000',
            '+38 (000) 000 00-00',
            '+380000000000',
            '+38 000 000 00 00',
            '+38 000 000 00-00',
            '+38 000 00 00 000',
            '+38 000 00-00 000',
            '0000000000',
            '000 000 00 00',
            '000 00 00 000',
            '         000 00 00 000',
            '000     00     00     000',
        ]
        for phone in raw_phones:
            result = self.service_fn(phone)
            self.assertEqual(result, expected_phone)

    def test_service_doesnt_normalizes_invalid_phone(self):
        raw_phones = [
            '+1 (050) 000 00-00',
            '3805000000000',
            '83 050-000-0000',
            '+38 050-00-00-00',
            '050 00 00 00',
            '+38 05000000 000',
        ]
        for phone in raw_phones:
            result = self.service_fn(phone)
            self.assertEqual(result, phone)
