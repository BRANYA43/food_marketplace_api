from utils import models
from utils.models.mixins import CreatedUpdatedMixin
from utils.tests import ApiTestCase


class AddressModelTest(ApiTestCase):
    model = models.Address

    def setUp(self) -> None:
        self.content_obj = self.create_test_user()
        self.data = dict(city='city', street='street', number='0', content_obj=self.content_obj)

    def test_models_inherit_created_updated_mixin(self):
        self.assert_is_subclass(self.model, CreatedUpdatedMixin)

    def test_expected_fields_are_required(self):
        self.assert_required_model_fields(
            self.model,
            self.data,
            ['city', 'street', 'number'],
        )

    def test_model_is_polymorphic(self):
        address1 = self.model.objects.create(**self.data)
        self.data['content_obj'] = address1
        address2 = self.model.objects.create(**self.data)

        self.assertEqual(address1.content_obj.id, self.content_obj.id)
        self.assertEqual(address2.content_obj.id, address1.id)
