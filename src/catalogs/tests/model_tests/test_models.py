from django.db import IntegrityError

from catalogs.models import Category
from utils.tests import ApiTestCase


class CategoryModelTest(ApiTestCase):
    model = Category

    def setUp(self) -> None:
        self.data = dict(
            name='Name',
        )

    def test_expected_fields_are_required(self):
        self.assert_required_model_fields(self.model, self.data, ['name'])

    def test_expected_fields_are_optional(self):
        self.assert_optional_model_fields(self.model, self.data, ['parent'])

    def test_name_field_is_unique(self):
        self.model.objects.create(**self.data)
        with self.assertRaisesRegex(IntegrityError, r'UNIQUE'):
            self.model.objects.create(**self.data)

    def test_is_parent_property(self):
        parent = self.model.objects.create(name='parent')
        child = self.model.objects.create(name='not parent', parent=parent)

        self.assertTrue(parent.is_parent)
        self.assertFalse(child.is_parent)

    def test_is_child_property(self):
        parent = self.model.objects.create(name='parent')
        child = self.model.objects.create(name='not parent', parent=parent)

        self.assertFalse(parent.is_child)
        self.assertTrue(child.is_child)
