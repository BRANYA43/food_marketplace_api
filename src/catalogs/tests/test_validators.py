import array
from unittest import TestCase

from django.core.exceptions import ValidationError

from catalogs.validators import validate_array_elements_uniqueness


class ArrayElementsUniquenessValidatorTest(TestCase):
    def test_validator_raises_error_for_invalid_array(self):
        invalid_array = array.array('i', (1, 2, 1))
        self.assertRaisesRegex(
            ValidationError,
            r'Array elements should be unique.',
            validate_array_elements_uniqueness,
            invalid_array,
        )

    def test_validator_doesnt_raise_error_for_array_consisting_of_1_element(self):
        valid_array = array.array('i', (1,))
        validate_array_elements_uniqueness(valid_array)  # not raise

    def test_validator_doesnt_raise_error_for_array_with_unique_elements(self):
        valid_array = array.array('i', (1, 2, 3))
        validate_array_elements_uniqueness(valid_array)  # not raise
