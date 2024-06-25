from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from catalogs import models


class CategoryModelTest(TestCase):
    def setUp(self) -> None:
        self.models_class = models.Category
        self.data = dict(
            name='books',
        )

    def test_name_field_is_required(self):
        del self.data['name']
        with self.assertRaisesRegex(ValidationError, r'This field cannot be blank.'):
            category = self.models_class.objects.create(**self.data)
            category.full_clean()

    def test_name_field_is_unique(self):
        self.models_class.objects.create(**self.data)
        with self.assertRaisesRegex(IntegrityError, r'UNIQUE'):
            self.models_class.objects.create(**self.data)

    def test_parent_field_is_option(self):
        category = self.models_class.objects.create(**self.data)
        category.full_clean()  # not raise

        self.assertIsNone(category.parent)

    def test_is_displayed_field_is_true_by_default(self):
        category = self.models_class.objects.create(**self.data)
        self.assertTrue(category.is_displayed)

    def test_string_representation_returns_name(self):
        category = self.models_class.objects.create(**self.data)
        self.assertEqual(str(category), category.name)
