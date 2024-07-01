from django.test import TestCase
from rest_framework.serializers import ModelSerializer

from catalogs import serializers, models


class CategoryRetrieveSerializerTest(TestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.CategoryRetrieveSerializer
        self.category = models.Category.objects.create(slug='plants', name='Plants')

    def test_serializer_inherits_model_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, ModelSerializer))

    def test_serializer_returns_expected_data(self):
        expected_data = {'id': self.category.id, 'name': self.category.name}
        serializer = self.serializer_class(self.category)

        self.assertEqual(serializer.data, expected_data)


class CategoryListSerializerTest(TestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.CategoryListSerializer

        self.parent_category = models.Category.objects.create(slug='plants', name='Plants')

    def test_serializer_inherits_model_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, ModelSerializer))

    def test_serializer_returns_expected_data(self):
        expected_data = [{'id': self.parent_category.id, 'name': self.parent_category.name, 'children': []}]
        qs = models.Category.objects.all()
        serializer = self.serializer_class(qs, many=True)

        self.assertEqual(serializer.data, expected_data)

    def test_serializer_returns_expected_data_with_nested_categories(self):
        child_category = models.Category.objects.create(
            slug='vegetables', name='Vegetables', parent=self.parent_category
        )
        sub_child_category = models.Category.objects.create(slug='tomato', name='Tomato', parent=child_category)
        expected_data = [
            {
                'id': self.parent_category.id,
                'name': self.parent_category.name,
                'children': [
                    {
                        'id': child_category.id,
                        'name': child_category.name,
                        'children': [{'id': sub_child_category.id, 'name': sub_child_category.name, 'children': []}],
                    }
                ],
            }
        ]
        qs = models.Category.objects.filter(parent=None)
        serializer = self.serializer_class(qs, many=True)
        self.assertEqual(serializer.data, expected_data)
