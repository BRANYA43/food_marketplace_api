from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from catalogs import serializers, models
from utils.tests import APITestCase


class AdvertSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.AdvertSerializer
        self.user = self.create_test_user()
        self.category = models.Category.objects.create(name='vegetables')
        self.address_data = dict(
            region='region',
            city='city',
            street='street',
            number='number',
        )
        self.advert_data = dict(
            user=self.user,
            category=self.category,
            title='Potato',
            price='100.00',
        )
        self.data = dict(
            user=self.user.id,
            category=self.category.id,
            title='Potato',
            price='100.00',
            address=self.address_data,
        )

    def test_serializer_inherits_model_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, ModelSerializer))

    def test_address_field_is_optional(self):
        del self.data['address']
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))  # not raise
        self.assertIsNone(serializer.data.get('address'))

    def test_serializer_creates_advert_without_address(self):
        del self.data['address']
        self.assertEqual(models.Advert.objects.count(), 0)
        self.assertEqual(models.AdvertAddress.objects.count(), 0)

        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(models.Advert.objects.count(), 1)
        self.assertEqual(models.AdvertAddress.objects.count(), 0)

        advert = models.Advert.objects.first()

        self.assertEqual(advert.user.id, self.data['user'])
        self.assertEqual(advert.category.id, self.data['category'])
        self.assertEqual(advert.title, self.data['title'])
        self.assertIsNone(advert.descr)
        self.assertEqual(advert.price, Decimal(self.data['price']))
        self.assertFalse(advert.use_pickup)
        self.assertFalse(advert.use_nova_post)
        self.assertTrue(advert.use_courier)

    def test_serializer_creates_advert_together_with_address(self):
        self.assertEqual(models.Advert.objects.count(), 0)
        self.assertEqual(models.AdvertAddress.objects.count(), 0)

        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(models.Advert.objects.count(), 1)
        self.assertEqual(models.AdvertAddress.objects.count(), 1)

        advert = models.Advert.objects.first()

        self.assertEqual(advert.user.id, self.data['user'])
        self.assertEqual(advert.category.id, self.data['category'])
        self.assertEqual(advert.title, self.data['title'])
        self.assertIsNone(advert.descr)
        self.assertEqual(advert.price, Decimal(self.data['price']))
        self.assertFalse(advert.use_pickup)
        self.assertFalse(advert.use_nova_post)
        self.assertTrue(advert.use_courier)

        address = models.AdvertAddress.objects.first()

        self.assertEqual(address.advert.id, address.id)
        self.assertEqual(address.region, self.address_data['region'])
        self.assertEqual(address.city, self.address_data['city'])
        self.assertIsNone(address.village)
        self.assertEqual(address.street, self.address_data['street'])
        self.assertEqual(address.number, self.address_data['number'])

    def test_serializer_updates_advert_without_address(self):
        update_data = dict(title='new title')
        advert = models.Advert.objects.create(**self.advert_data)

        self.assertEqual(models.Advert.objects.count(), 1)
        self.assertEqual(models.AdvertAddress.objects.count(), 0)
        self.assertNotEqual(advert.title, update_data['title'])

        serializer = self.serializer_class(advert, update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(models.Advert.objects.count(), 1)
        self.assertEqual(models.AdvertAddress.objects.count(), 0)
        self.assertEqual(advert.title, update_data['title'])

    def test_serializer_updates_advert_and_create_address(self):
        update_data = dict(
            title='new title',
            address=self.address_data,
        )
        advert = models.Advert.objects.create(**self.advert_data)

        self.assertEqual(models.Advert.objects.count(), 1)
        self.assertEqual(models.AdvertAddress.objects.count(), 0)
        self.assertNotEqual(advert.title, update_data['title'])

        serializer = self.serializer_class(advert, update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(models.Advert.objects.count(), 1)
        self.assertEqual(models.AdvertAddress.objects.count(), 1)
        self.assertEqual(advert.title, update_data['title'])

        address = models.AdvertAddress.objects.first()

        self.assertEqual(address.region, self.address_data['region'])
        self.assertEqual(address.city, self.address_data['city'])
        self.assertIsNone(address.village)
        self.assertEqual(address.street, self.address_data['street'])
        self.assertEqual(address.number, self.address_data['number'])

    def test_serializer_updates_advert_together_with_address(self):
        update_data = dict(
            title='new title',
            address=dict(number='new number'),
        )
        advert = models.Advert.objects.create(**self.advert_data)
        address = models.AdvertAddress.objects.create(**self.address_data, advert=advert)
        self.assertEqual(models.Advert.objects.count(), 1)
        self.assertEqual(models.AdvertAddress.objects.count(), 1)
        self.assertNotEqual(advert.title, update_data['title'])
        self.assertNotEqual(address.number, update_data['address']['number'])

        serializer = self.serializer_class(advert, update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        address.refresh_from_db()

        self.assertEqual(models.Advert.objects.count(), 1)
        self.assertEqual(models.AdvertAddress.objects.count(), 1)
        self.assertEqual(advert.title, update_data['title'])
        self.assertEqual(address.number, update_data['address']['number'])

    def test_serializer_returns_expected_data_without_address(self):
        del self.data['address']
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        advert = models.Advert.objects.first()
        expected_data = dict(
            id=advert.id,
            user=advert.user.id,
            category=advert.category.id,
            title=advert.title,
            descr=advert.descr,
            price=str(advert.price),
            address=getattr(advert, 'address', None),
            use_pickup=advert.use_pickup,
            use_nova_post=advert.use_nova_post,
            use_courier=advert.use_courier,
        )

        self.assertDictEqual(serializer.data, expected_data)

    def test_serializer_returns_expected_data_with_address(self):
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        advert = models.Advert.objects.first()
        address = advert.address
        expected_data = dict(
            id=advert.id,
            user=advert.user.id,
            category=advert.category.id,
            title=advert.title,
            descr=advert.descr,
            price=str(advert.price),
            address=dict(
                region=address.region,
                city=address.city,
                village=address.village,
                street=address.street,
                number=address.number,
            ),
            use_pickup=advert.use_pickup,
            use_nova_post=advert.use_nova_post,
            use_courier=advert.use_courier,
        )

        self.assertDictEqual(serializer.data, expected_data)


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
