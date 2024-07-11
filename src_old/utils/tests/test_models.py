from django.core.exceptions import ValidationError

from utils import models
from utils.tests import APITestCase


class AddressModelTest(APITestCase):
    def setUp(self) -> None:
        self.model_class = models.Address
        self.data = dict(
            region='region',
            city='city',
            street='street',
            number='0',
        )

    def test_model_inherits_create_updated_mixin(self):
        self.assertTrue(issubclass(self.model_class, models.CreatedUpdatedMixin))

    def test_region_field_is_required(self):
        del self.data['region']
        with self.assertRaisesRegex(ValidationError, r'This field cannot be blank'):
            address = self.model_class.objects.create(**self.data)
            address.full_clean()

    def test_city_field_is_required(self):
        del self.data['city']
        with self.assertRaisesRegex(ValidationError, r'This field cannot be blank'):
            address = self.model_class.objects.create(**self.data)
            address.full_clean()

    def test_street_field_is_required(self):
        del self.data['street']
        with self.assertRaisesRegex(ValidationError, r'This field cannot be blank'):
            address = self.model_class.objects.create(**self.data)
            address.full_clean()

    def test_number_field_is_required(self):
        del self.data['number']
        with self.assertRaisesRegex(ValidationError, r'This field cannot be blank'):
            address = self.model_class.objects.create(**self.data)
            address.full_clean()

    def test_village_is_optional(self):
        address = self.model_class.objects.create(**self.data)
        address.full_clean()  # not raise

    def test_string_representation_return_correct_format(self):
        # without village
        expected_value = (
            f"Address({self.data['region']}, {self.data['city']}, {self.data['street']}, " f"{self.data['number']})"
        )
        address = self.model_class.objects.create(**self.data)
        self.assertEqual(str(address), expected_value)

        # with village
        self.data['village'] = 'village'
        expected_value = (
            f"Address({self.data['region']}, {self.data['city']}, {self.data['village']}, "
            f"{self.data['street']}, {self.data['number']})"
        )
        address = self.model_class.objects.create(**self.data)
        self.assertEqual(str(address), expected_value)
