from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from catalogs import serializers, models
from utils.tests import APITestCase


class AdvertAddressSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.AdvertAddressSerializer
        self.address_model_class = models.AdvertAddress
        self.user = self.create_test_user()
        self.category = models.Category.objects.create(name='vegetables')
        self.advert = models.Advert.objects.create(
            user=self.user,
            category=self.category,
            title='Potato',
            price='100.00',
        )
        self.data = dict(
            region='region',
            city='city',
            street='street',
            number='0',
        )

    def test_serializer_inherit_model_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, ModelSerializer))

    def test_advert_field_is_optional(self):
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_advert_field_is_write_only(self):
        self.data['advert'] = self.advert.pk
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid())

        self.assertIsNone(serializer.data.get('user'))

    def test_region_field_is_required(self):
        del self.data['region']
        serializer = self.serializer_class(data=self.data)
        with self.assertRaisesRegex(ValidationError, r"code='required'"):
            serializer.is_valid(raise_exception=True)

    def test_city_field_is_required(self):
        del self.data['city']
        serializer = self.serializer_class(data=self.data)
        with self.assertRaisesRegex(ValidationError, r"code='required'"):
            serializer.is_valid(raise_exception=True)

    def test_street_field_is_required(self):
        del self.data['street']
        serializer = self.serializer_class(data=self.data)
        with self.assertRaisesRegex(ValidationError, r"code='required'"):
            serializer.is_valid(raise_exception=True)

    def test_number_field_is_required(self):
        del self.data['number']
        serializer = self.serializer_class(data=self.data)
        with self.assertRaisesRegex(ValidationError, r"code='required'"):
            serializer.is_valid(raise_exception=True)

    def test_village_field_is_optional(self):
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_creates_address(self):
        self.assertEqual(self.address_model_class.objects.count(), 0)

        self.data['advert'] = self.advert.pk
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        address = self.address_model_class.objects.get(advert=self.advert)
        del self.data['advert']
        for field, value in self.data.items():
            self.assertEqual(getattr(address, field, value), self.data[field])

    def test_serializer_updates_address(self):
        self.data['advert'] = self.advert
        address = self.address_model_class.objects.create(**self.data)

        update_data = dict(region='new region')
        serializer = self.serializer_class(address, update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        db_address = self.address_model_class.objects.get(advert=self.advert)

        self.assertEqual(db_address.region, update_data['region'])

    def test_serializer_returns_expected_data(self):
        self.data['advert'] = self.advert.pk

        expected_data = dict(
            region=self.data['region'],
            city=self.data['city'],
            village=None,
            street=self.data['street'],
            number=self.data['number'],
        )

        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertDictEqual(serializer.data, expected_data)


class CategoryRetrieveSerializerTest(TestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.CategoryRetrieveSerializer
        self.category = models.Category.objects.create(name='Plants')

    def test_serializer_inherits_model_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, ModelSerializer))

    def test_serializer_returns_expected_data(self):
        expected_data = {'id': self.category.id, 'name': self.category.name}
        serializer = self.serializer_class(self.category)

        self.assertEqual(serializer.data, expected_data)


class CategoryListSerializerTest(TestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.CategoryListSerializer

        self.parent_category = models.Category.objects.create(name='Plants')

    def test_serializer_inherits_model_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, ModelSerializer))

    def test_serializer_returns_expected_data(self):
        expected_data = [{'id': self.parent_category.id, 'name': self.parent_category.name, 'children': []}]
        qs = models.Category.objects.all()
        serializer = self.serializer_class(qs, many=True)

        self.assertEqual(serializer.data, expected_data)

    def test_serializer_returns_expected_data_with_nested_categories(self):
        child_category = models.Category.objects.create(name='Vegetables', parent=self.parent_category)
        sub_child_category = models.Category.objects.create(name='Tomato', parent=child_category)
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
