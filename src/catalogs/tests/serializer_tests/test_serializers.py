from decimal import Decimal

from catalogs.models import Category
from catalogs.models.models import Advert
from catalogs.serializers import CategoryListSerializer
from catalogs.serializers.serializers import (
    CategorySerializer,
    AdvertListSerializer,
    AdvertRetrieveSerializer,
    AdvertCreateSerializer,
    AdvertUpdateSerializer,
)
from utils.models import Address
from utils.tests import ApiTestCase
from utils.tests.cases import SerializerTestCase
from utils.serializers.mixins import AddressCreateUpdateMixin


class AdvertUpdateSerializerTest(SerializerTestCase):
    serializer_class = AdvertUpdateSerializer
    advert_model = Advert
    address_model = Address

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)

        self.input_data = dict(name='New name')

        self.output_data = dict(
            id=1,
            owner=self.owner.id,
            category=self.category.id,
            name=self.input_data['name'],
            descr=None,
            price=str(self.advert.price),
            quantity=self.advert.quantity,
            pickup=self.advert.pickup,
            nova_post=self.advert.nova_post,
            courier=self.advert.courier,
            address={},
        )

        self.input_address_data = dict(city='new city', street='new stree', number='new number')

    def test_serializer_inherits_mixins(self):
        self.assert_is_subclass(self.serializer_class, AddressCreateUpdateMixin)

    def test_expected_fields_are_read_only(self):
        self.assert_fields_are_read_only(self.serializer_class, ['id', 'owner'])

    def test_serializer_updates_advert_without_address(self):
        self.assertEqual(self.address_model.objects.count(), 0)
        self.assert_model_instance(self.advert, self.input_data, equal=False)

        self.create_serializer(
            self.serializer_class,
            self.input_data,
            save=True,
            partial=True,
            instance=self.advert,
        )

        self.assertEqual(self.address_model.objects.count(), 0)
        self.assert_model_instance(self.advert, self.input_data)

    def test_serializer_updates_advert_with_address(self):
        address = self.create_test_address(self.advert)
        self.advert.refresh_from_db()

        self.assert_model_instance(address, self.input_address_data, equal=False)
        self.assert_model_instance(self.advert, self.input_data, equal=False)

        self.create_serializer(
            self.serializer_class,
            dict(**self.input_data, address=self.input_address_data),
            save=True,
            partial=True,
            instance=self.advert,
        )

        address.refresh_from_db()
        self.assert_model_instance(address, self.input_address_data)
        self.assert_model_instance(self.advert, self.input_data)

    def test_serializer_updates_advert_and_create_address(self):
        self.assertEqual(self.address_model.objects.count(), 0)

        self.assert_model_instance(
            self.advert,
            self.input_data,
            equal=False,
        )

        self.create_serializer(
            self.serializer_class,
            dict(**self.input_data, address=self.input_address_data),
            save=True,
            partial=True,
            instance=self.advert,
        )

        self.assertEqual(self.address_model.objects.count(), 1)

        address = self.address_model.objects.get(object_id=self.advert.id)
        self.assert_model_instance(address, self.input_address_data)

        self.assert_model_instance(self.advert, self.input_data)

    def test_serializer_returns_expected_data_without_address(self):
        self.assert_output_serializer_data(
            self.serializer_class,
            input_data=self.input_data,
            output_data=self.output_data,
            save=True,
            partial=True,
            instance=self.advert,
        )

    def test_serializer_returns_expected_data_with_address(self):
        self.output_data['address'] = self.input_address_data
        self.assert_output_serializer_data(
            self.serializer_class,
            input_data=dict(**self.input_data, address=self.input_address_data),
            output_data=self.output_data,
            save=True,
            partial=True,
            instance=self.advert,
        )


class AdvertCreateSerializerTest(SerializerTestCase):
    serializer_class = AdvertCreateSerializer
    advert_model = Advert
    address_model = Address

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()

        self.input_data = dict(
            owner=self.owner.id,
            category=self.category.id,
            name='name',
            price=Decimal('100.00'),
        )

        self.output_data = dict(
            id=1,
            owner=self.owner.id,
            category=self.category.id,
            name=self.input_data['name'],
            descr=None,
            price=str(self.input_data['price']),
            quantity=1,
            pickup=False,
            nova_post=False,
            courier=True,
            address={},
        )

        self.input_address_data = dict(
            city='city',
            street='street',
            number='number',
        )

    def test_serializer_inherits_mixins(self):
        self.assert_is_subclass(self.serializer_class, AddressCreateUpdateMixin)

    def test_expected_fields_are_read_only(self):
        self.assert_fields_are_read_only(
            self.serializer_class,
            ['id'],
        )

    def test_serializer_creates_advert_without_address(self):
        self.assertEqual(self.advert_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

        self.create_serializer(
            self.serializer_class,
            input_data=self.input_data,
            save=True,
        )

        self.assertEqual(self.advert_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 0)

        advert = self.advert_model.objects.first()
        self.assert_model_instance(advert, self.input_data)

    def test_serializer_creates_advert_with_address(self):
        self.input_data['address'] = self.input_address_data
        self.input_data['pickup'] = True

        self.output_data['address'] = self.input_address_data
        self.output_data['pickup'] = True

        self.assertEqual(self.advert_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

        self.create_serializer(
            self.serializer_class,
            input_data=self.input_data,
            save=True,
        )

        self.assertEqual(self.advert_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 1)

        advert = self.advert_model.objects.first()
        self.input_data.pop('address')
        self.assert_model_instance(advert, self.input_data)

        address = advert.address.first()
        self.assert_model_instance(address, self.input_address_data)

    def test_serializer_returns_expected_data_without_address(self):
        self.assert_output_serializer_data(
            self.serializer_class,
            input_data=self.input_data,
            output_data=self.output_data,
            save=True,
        )

    def test_serializer_returns_expected_data_with_address(self):
        self.input_data['address'] = self.input_address_data
        self.input_data['pickup'] = True

        self.output_data['address'] = self.input_address_data
        self.output_data['pickup'] = True

        self.assert_output_serializer_data(
            self.serializer_class,
            input_data=self.input_data,
            output_data=self.output_data,
            save=True,
        )


class AdvertRetrieveSerializerTest(SerializerTestCase):
    serializer_class = AdvertRetrieveSerializer
    model = Advert

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)

        self.output_data = dict(
            id=self.advert.id,
            owner=self.owner.id,
            category=self.advert.category.id,
            name=self.advert.name,
            descr=self.advert.descr,
            price=str(self.advert.price),
            quantity=self.advert.quantity,
            pickup=False,
            nova_post=False,
            courier=True,
            address={},
        )

    def test_expected_fields_are_read_only(self):
        self.assert_fields_are_read_only(
            self.serializer_class,
            [
                'id',
                'owner',
                'category',
                'name',
                'descr',
                'price',
                'quantity',
                'pickup',
                'nova_post',
                'courier',
                'address',
            ],
        )

    def test_serializer_returns_expected_data_without_address(self):
        self.assert_output_serializer_data(
            self.serializer_class,
            instance=self.advert,
            input_data={},
            output_data=self.output_data,
        )

    def test_serializer_returns_expected_data_with_address(self):
        address = self.create_test_address(self.advert)
        address_data = dict(
            city=address.city,
            street=address.street,
            number=address.number,
        )
        self.advert.refresh_from_db()
        self.output_data['address'] = address_data

        self.assert_output_serializer_data(
            self.serializer_class,
            instance=self.advert,
            input_data={},
            output_data=self.output_data,
        )


class AdvertListSerializerTest(SerializerTestCase):
    serializer_class = AdvertListSerializer
    model = Advert

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)

    def test_expected_fields_are_read_only(self):
        self.assert_fields_are_read_only(
            self.serializer_class,
            ['id', 'name', 'category', 'price'],
        )

    def test_serializer_returns_expected_data(self):
        self.serializer_class()
        self.assert_output_serializer_data(
            self.serializer_class,
            instance=self.advert,
            input_data={},
            output_data=dict(
                id=self.advert.id,
                name=self.advert.name,
                category=self.advert.category.id,
                price=str(self.advert.price),
            ),
        )


class CategorySerializerTest(ApiTestCase):
    serializer_class = CategorySerializer
    model = Category

    def test_serializer_returns_expected_data_for_some_category(self):
        self.create_test_category(name='Category 1')
        self.create_test_category(name='Category 2')

        expected_data = [dict(id=category.id, name=category.name) for category in self.model.objects.all()]

        serializer = self.serializer_class(self.model.objects.filter(children=None), many=True)

        self.assertSequenceEqual(serializer.data, expected_data)

    def test_serializer_returns_expected_data_for_category(self):
        category = self.create_test_category(name='Category 1')

        expected_data = dict(id=category.id, name=category.name)

        serializer = self.serializer_class(category)

        self.assertSequenceEqual(serializer.data, expected_data)


class CategoryListSerializerTest(ApiTestCase):
    serializer_class = CategoryListSerializer
    model = Category

    def get_expected_category_data(self, categories):
        ret = []
        for category in categories:
            ret.append(
                dict(
                    id=category.id,
                    name=category.name,
                    sub_categories=self.get_expected_category_data(category.children.all()),
                )
            )
        return ret

    def test_serializer_returns_expected_data_for_some_categories(self):
        self.create_test_category(name='Category 1')
        self.create_test_category(name='Category 2')
        self.create_test_category(name='Category 3')

        expected_data = self.get_expected_category_data(self.model.objects.filter(parent=None))

        serializer = self.serializer_class(self.model.objects.filter(parent=None), many=True)

        self.assertSequenceEqual(serializer.data, expected_data)

    def test_serializer_returns_expected_data_for_some_categories_with_children(self):
        food = self.create_test_category(name='Food')
        vegetables = self.create_test_category(name='Vegetables', parent=food)
        self.create_test_category(name='Tomato', parent=vegetables)
        self.create_test_category(name='Fruits', parent=food)
        self.create_test_category('All For Home')

        expected_data = self.get_expected_category_data(self.model.objects.filter(parent=None))

        serializer = self.serializer_class(self.model.objects.filter(parent=None), many=True)

        self.assertSequenceEqual(serializer.data, expected_data)
