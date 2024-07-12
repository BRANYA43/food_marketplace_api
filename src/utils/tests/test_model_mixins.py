from utils import models
from utils.tests import AbstractModelTestCase


class CreatedUpdatedMixinTest(AbstractModelTestCase):
    abstract_model = models.CreatedUpdatedMixin

    def test_updated_at_field_sets_value_auto(self):
        instance = self.model.objects.create()
        old_update_at = instance.updated_at
        instance.save()

        self.assertNotEqual(old_update_at, instance.updated_at)

    def test_created_at_field_sets_value_auto_only_once(self):
        instance = self.model.objects.create()
        old_create_at = instance.created_at
        instance.save()
        self.assertEqual(old_create_at, instance.created_at)
