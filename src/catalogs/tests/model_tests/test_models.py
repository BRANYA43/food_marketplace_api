from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from catalogs.models import Category
from catalogs.models.models import Advert, Image
from utils.models.mixins import CreatedUpdatedMixin
from utils.models import Address
from utils.tests.cases import ModelTestCase
from utils.tests.cases.media_case import MediaTestCase

User = get_user_model()


class ImageModelTest(MediaTestCase):
    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(owner=self.owner, category=self.category)
        self.file = self.get_image_simple_uploaded_file('image.png')
        self.data = dict(
            advert=self.advert,
            file=self.file,
            type=Image.Type.MAIN,
        )

    def test_model_returns_expected_str_representation(self):
        image = Image.objects.create(**self.data)
        self.assertEqual(str(image), f'{self.advert.name} {image.type} image')

    def test_model_save_file_by_expected_path(self):
        image = Image.objects.create(**self.data)
        date = datetime.now()
        month = f'0{date.month}' if date.month < 10 else str(date.month)
        day = f'0{date.day}' if date.day < 10 else str(date.day)
        self.assertEqual(image.file.url, f'/media/images/{date.year}/{month}/{day}/{self.file.name}')

    def test_model_doesnt_save_main_image_if_advert_already_has_main_image(self):
        Image.objects.create(**self.data)
        with self.assertRaisesRegex(ValidationError, r'Advert already has main image.'):
            image = Image(**self.data)
            image.full_clean()

    def test_model_saves_some_extra_images_for_advert(self):
        Image.objects.create(**self.data)
        self.data['type'] = Image.Type.EXTRA
        for i in range(3):
            Image.objects.create(**self.data)


class AdvertModelTest(ModelTestCase):
    model = Advert

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.data = dict(
            owner=self.owner,
            category=self.category,
            name='New name',
            price=100,
        )

    def test_model_inherit_expected_mixins(self):
        self.assert_is_subclass(self.model, CreatedUpdatedMixin)

    def test_expected_fields_are_required(self):
        self.assert_required_fields(
            self.model,
            ['owner', 'category', 'name', 'price'],
        )

    def test_expected_fields_are_optional(self):
        self.assert_optional_fields(
            self.model,
            ['descr'],
        )

    def test_expected_fields_have_default_values(self):
        self.assert_fields_have_default_value(
            self.model,
            dict(quantity=1, pickup=False, nova_post=False, courier=True),
        )

    def test_expected_fields_have_specified_relation(self):
        self.assert_fields_have_specified_relation(
            self.model,
            [
                dict(name='owner', to=User, relation='many_to_one', related_name='adverts'),
                dict(name='category', to=Category, relation='many_to_one', related_name='adverts'),
                dict(name='address', to=Address, relation='one_to_many'),
            ],
        )

    def test_expected_fields_have_specified_max_length(self):
        self.assert_fields_have_specified_max_length(self.model, dict(name=70, descr=1024))

    def test_expected_decimal_field_is_set_correct(self):
        self.assert_decimal_fields(self.model, [dict(name='price', max_digits=12, decimal_places=2)])

    def test_price_field_must_be_gte_0(self):
        self.data['price'] = -1
        advert = self.model(**self.data)
        with self.assertRaisesRegex(ValidationError, r'Ensure this value is greater than or equal to 0.'):
            advert.full_clean()

    def test_quantity_field_must_be_gt_0(self):
        self.data['quantity'] = 0
        advert = self.model(**self.data)
        with self.assertRaisesRegex(ValidationError, r'quantity.+Ensure this value is greater than or equal to 1'):
            advert.full_clean()

    def test_one_of_pickup_nova_post_courier_fields_must_be_true(self):
        self.data.update(dict(pickup=False, nova_post=False, courier=False))
        advert = self.model(**self.data)
        with self.assertRaisesRegex(
            ValidationError, r'One of the fields "pickup", "nova_post", "courier" must be True.'
        ):
            advert.full_clean()

    def test_pickup_address_must_be_if_pickup_is_true(self):
        self.data.update(dict(pickup=True))
        advert = self.model(**self.data)
        with self.assertRaisesRegex(ValidationError, r'The "pickup_address" field must be if "pickup" field is True.'):
            advert.full_clean()


class CategoryModelTest(ModelTestCase):
    model = Category

    def setUp(self) -> None:
        self.data = dict(
            name='Name',
        )

    def test_expected_fields_are_required(self):
        self.assert_required_fields(self.model, ['name'])

    def test_expected_fields_are_optional(self):
        self.assert_optional_fields(self.model, ['parent'])

    def test_expected_fields_are_unique(self):
        self.assert_unique_fields(self.model, ['name'])

    def test_expected_fields_have_specified_max_length(self):
        self.assert_fields_have_specified_max_length(self.model, dict(name=100))

    def test_expected_fields_have_specified_relation(self):
        self.assert_fields_have_specified_relation(
            self.model,
            [dict(name='parent', to=self.model, relation='many_to_one', related_name='children')],
        )

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
