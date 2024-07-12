from utils import models
from utils.tests import ApiTestCase


class AddressModelTest(ApiTestCase):
    model = models.Address

    def setUp(self) -> None:
        self.content_obj = self.create_test_user()
        self.data = dict(region='region', city='city', street='street', number='0', content_obj=self.content_obj)

    def test_region_field_is_required(self):
        self.assert_required_model_field(self.model, 'region', self.data, 'region.+This field cannot be blank.')

    def test_city_field_is_required(self):
        self.assert_required_model_field(self.model, 'city', self.data, 'city.+This field cannot be blank.')

    def test_street_field_is_required(self):
        self.assert_required_model_field(self.model, 'street', self.data, 'street.+This field cannot be blank.')

    def test_number_field_is_required(self):
        self.assert_required_model_field(self.model, 'number', self.data, 'number.+This field cannot be blank.')

    def test_village_field_is_optional(self):
        self.assert_optional_model_field(self.model, 'village', self.data)

    def test_model_is_polymorphic(self):
        address1 = self.model.objects.create(**self.data)
        self.data['content_obj'] = address1
        address2 = self.model.objects.create(**self.data)

        self.assertEqual(address1.content_obj.id, self.content_obj.id)
        self.assertEqual(address2.content_obj.id, address1.id)
