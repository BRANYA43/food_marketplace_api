import re


class UkrainianPhoneNumberNormalizer:
    """Normalizer ukrainian phone number to one format: +38 (012) 345 6789"""

    def __init__(self):
        self.pattern = re.compile(r'^(38)?(\d{3})(\d{3})(\d{4})$')

    def __call__(self, phone: str, *args, **kwargs):
        clear_phone = self._get_clear_phone(phone)
        try:
            _, operator, first, second = self.pattern.match(clear_phone).groups()
        except (ValueError, AttributeError):
            pass
        else:
            phone = f'+38 ({operator}) {first} {second}'

        return phone

    @staticmethod
    def _get_clear_phone(phone: str) -> str:
        return ''.join(re.findall(r'\d+', phone))
