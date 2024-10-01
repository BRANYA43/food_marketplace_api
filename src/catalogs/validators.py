from django.core.exceptions import ValidationError


def validate_array_elements_uniqueness(value):
    if len(value) != len(set(value)):
        raise ValidationError(
            'Array elements should be unique.',
            'invalid_array_element_uniqueness',
        )
