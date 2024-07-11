import re


def normalize_phone_to_ukrainian_format(phone: str):
    try:
        _, operator, first, second = re.match(r'^(38)?(\d{3})(\d{3})(\d{4})$', _get_clear_phone(phone)).groups()  # type: ignore
    except (ValueError, AttributeError):
        pass
    else:
        phone = f'+38 ({operator}) {first} {second}'

    return phone


def _get_clear_phone(phone: str) -> str:
    phone = ''.join(re.findall(r'\d+', phone))
    return phone
