from utils import models
from utils.models.mixins import CreatedUpdatedMixin
from utils.tests.cases import BaseTestCase


class AddressModelTest(BaseTestCase):
    model = models.Address

    def setUp(self) -> None:
        self.content_obj = self.create_test_user()
        self.data = dict(
            city='city',
            street='street',
            number='0',
            content_obj=self.content_obj,
        )

    def test_models_inherit_mixin(self):
        self.assert_is_subclass(self.model, CreatedUpdatedMixin)

    def test_model_is_polymorphic(self):
        address1 = self.model.objects.create(**self.data)
        self.data['content_obj'] = address1
        address2 = self.model.objects.create(**self.data)

        self.assertEqual(address1.content_obj.id, self.content_obj.id)
        self.assertEqual(address2.content_obj.id, address1.id)
