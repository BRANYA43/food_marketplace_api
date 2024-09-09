from utils.models.mixins import CreatedUpdatedMixin
from utils.tests.cases import BaseTestCase


class CreatedUpdatedMixinTest(BaseTestCase):
    mixin = CreatedUpdatedMixin

    def test_updated_at_field_sets_value_auto_after_update(self):
        field = self.mixin.updated_at.field
        self.assertTrue(field.auto_now)

    def test_created_at_field_sets_value_auto_after_creation(self):
        field = self.mixin.created_at.field
        self.assertTrue(field.auto_now_add)
