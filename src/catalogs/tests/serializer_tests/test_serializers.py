from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from catalogs.models import Category, Advert, Image
from catalogs.serializers import (
    CategoryListSerializer,
    CategorySerializer,
    AdvertListSerializer,
    AdvertRetrieveSerializer,
    AdvertCreateSerializer,
    AdvertUpdateSerializer,
    ImageMultipleCreateSerializer,
    ImageMultipleDeleteSerializer,
)
from utils.models import Address
from utils.tests.cases import BaseTestCase, MediaTestCase
from utils.serializers.mixins import AddressCreateUpdateMixin


class ImageMultipleDeleteSerializerTest(MediaTestCase):
    serializer_class = ImageMultipleDeleteSerializer

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)
        self.main_image = self.create_test_image(self.advert)
        self.extra_image = self.create_test_image(self.advert, type=Image.Type.EXTRA)

        self.data = dict(
            advert=self.advert.id,
            files=[str(self.extra_image.file)],
        )

    def test_serializer_deletes_image(self):
        self.assertEqual(Image.objects.count(), 2)

        serializer = self.create_serializer(
            self.serializer_class,
            data=self.data,
        )
        serializer.delete()

        self.assertEqual(Image.objects.count(), 1)

    def test_serializer_doesnt_delete_non_existent_image(self):
        self.assertEqual(Image.objects.count(), 2)

        self.data['files'].append('non_existent_img.png')
        with self.assertRaisesRegex(
            DRFValidationError,
            r"Advert have not followed images with the names: \['non_existent_img.png'\].",
        ):
            self.create_serializer(
                self.serializer_class,
                data=self.data,
            )

        self.assertEqual(Image.objects.count(), 2)


class ImageMultipleCreateSerializerTest(MediaTestCase):
    serializer_class = ImageMultipleCreateSerializer

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)
        self.main_file = self.get_image_simple_uploaded_file('main_image.png')
        self.extra_file = self.get_image_simple_uploaded_file('extra_image.png')

        self.data = dict(
            advert=self.advert.id,
            files=[self.main_file, self.extra_file],
            types=[Image.Type.MAIN, Image.Type.EXTRA],
        )

    def test_serializer_creates_images(self):
        self.assertEqual(Image.objects.count(), 0)

        self.create_serializer(
            self.serializer_class,
            data=self.data,
            save=True,
        )

        self.assertEqual(Image.objects.count(), 2)

        main_image = Image.objects.get(advert=self.advert, type=Image.Type.MAIN)
        extra_image = Image.objects.get(advert=self.advert, type=Image.Type.EXTRA)

        self.assertIn(self.main_file.name, main_image.file.name)
        self.assertIn(self.extra_file.name, extra_image.file.name)

    def test_serializer_cancels_all_created_images_and_doesnt_create_other_images_if_error_is_raised(self):
        self.data['files'].append(self.main_file)
        self.data['types'].append(Image.Type.MAIN)

        self.assertEqual(Image.objects.count(), 0)

        with self.assertRaises(DjangoValidationError):
            self.create_serializer(
                self.serializer_class,
                data=self.data,
                save=True,
            )

        self.assertEqual(Image.objects.count(), 0)

    def test_serializer_raises_error_if_files_and_types_count_mismatch(self):
        self.data['types'] = [self.data['types'][0]]
        with self.assertRaisesRegex(DRFValidationError, 'File quantity should match type quantity.'):
            self.create_serializer(
                self.serializer_class,
                data=self.data,
                save=True,
            )


class AdvertUpdateSerializerTest(BaseTestCase):
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

    def test_serializer_updates_advert_without_address(self):
        self.assertEqual(self.address_model.objects.count(), 0)
        self.assert_model_instance(self.advert, self.input_data, equal=False)

        self.create_serializer(
            self.serializer_class,
            data=self.input_data,
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
            data=dict(**self.input_data, address=self.input_address_data),
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
            data=dict(**self.input_data, address=self.input_address_data),
            save=True,
            partial=True,
            instance=self.advert,
        )

        self.assertEqual(self.address_model.objects.count(), 1)

        address = self.address_model.objects.get(object_id=self.advert.id)
        self.assert_model_instance(address, self.input_address_data)

        self.assert_model_instance(self.advert, self.input_data)

    def test_serializer_returns_expected_data_without_address(self):
        self.assert_serializer_output_data(
            self.serializer_class,
            data=self.input_data,
            expected_data=self.output_data,
            save=True,
            partial=True,
            instance=self.advert,
        )

    def test_serializer_returns_expected_data_with_address(self):
        self.output_data['address'] = self.input_address_data
        self.assert_serializer_output_data(
            self.serializer_class,
            data=dict(**self.input_data, address=self.input_address_data),
            expected_data=self.output_data,
            save=True,
            partial=True,
            instance=self.advert,
        )


class AdvertCreateSerializerTest(BaseTestCase):
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

    def test_serializer_creates_advert_without_address(self):
        self.assertEqual(self.advert_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

        self.create_serializer(
            self.serializer_class,
            data=self.input_data,
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
            data=self.input_data,
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
        self.assert_serializer_output_data(
            self.serializer_class,
            data=self.input_data,
            expected_data=self.output_data,
            save=True,
        )

    def test_serializer_returns_expected_data_with_address(self):
        self.input_data['address'] = self.input_address_data
        self.input_data['pickup'] = True

        self.output_data['address'] = self.input_address_data
        self.output_data['pickup'] = True

        self.assert_serializer_output_data(
            self.serializer_class,
            data=self.input_data,
            expected_data=self.output_data,
            save=True,
        )


class AdvertRetrieveSerializerTest(MediaTestCase, BaseTestCase):
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
            main_image=None,
            extra_images=[],
        )

    def test_serializer_returns_expected_data(self):
        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.advert,
            expected_data=self.output_data,
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

        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.advert,
            expected_data=self.output_data,
        )

    def test_serializer_returns_expected_data_with_main_image(self):
        main_image = self.create_test_image(self.advert)
        self.advert.refresh_from_db()
        self.output_data['main_image'] = str(main_image.file)
        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.advert,
            expected_data=self.output_data,
        )

    def test_serializer_returns_expected_data_with_extra_images(self):
        extra_image = self.create_test_image(self.advert, type=Image.Type.EXTRA)
        self.advert.refresh_from_db()
        self.output_data['extra_images'] = [str(extra_image.file)]
        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.advert,
            expected_data=self.output_data,
        )


class AdvertListSerializerTest(MediaTestCase, BaseTestCase):
    serializer_class = AdvertListSerializer
    model = Advert

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)

    def test_serializer_returns_expected_data_without_main_image(self):
        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.advert,
            expected_data=dict(
                id=self.advert.id,
                name=self.advert.name,
                category=self.advert.category.id,
                price=str(self.advert.price),
                main_image=None,
            ),
        )

    def test_serializer_returns_expected_data_with_main_image(self):
        main_image = self.create_test_image(self.advert)
        self.advert.refresh_from_db()
        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.advert,
            expected_data=dict(
                id=self.advert.id,
                name=self.advert.name,
                category=self.advert.category.id,
                price=str(self.advert.price),
                main_image=str(main_image.file),
            ),
        )


class CategorySerializerTest(BaseTestCase):
    serializer_class = CategorySerializer
    model = Category

    def test_serializer_returns_data_with_some_category(self):
        self.create_test_category(name='Category 1')
        self.create_test_category(name='Category 2')

        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.model.objects.filter(children=None),
            many=True,
            expected_data=[dict(id=category.id, name=category.name) for category in self.model.objects.all()],
        )

    def test_serializer_returns_data_with_one_category(self):
        category = self.create_test_category(name='Category 1')

        self.assert_serializer_output_data(
            self.serializer_class,
            instance=category,
            expected_data=dict(id=category.id, name=category.name),
        )


class CategoryListSerializerTest(BaseTestCase):
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

        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.model.objects.filter(parent=None),
            expected_data=self.get_expected_category_data(self.model.objects.filter(parent=None)),
            many=True,
        )

    def test_serializer_returns_expected_data_for_some_categories_with_children(self):
        food = self.create_test_category(name='Food')
        vegetables = self.create_test_category(name='Vegetables', parent=food)
        self.create_test_category(name='Tomato', parent=vegetables)
        self.create_test_category(name='Fruits', parent=food)
        self.create_test_category('All For Home')

        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.model.objects.filter(parent=None),
            expected_data=self.get_expected_category_data(self.model.objects.filter(parent=None)),
            many=True,
        )
