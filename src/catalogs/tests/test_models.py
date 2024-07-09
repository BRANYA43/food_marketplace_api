import shutil
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TransactionTestCase, TestCase, override_settings

from catalogs import models
from utils.tests import APITestCase


class AdvertAddressModelTest(APITestCase):
    def setUp(self):
        self.model_class = models.AdvertAddress
        self.user = self.create_test_user()
        self.category = models.Category.objects.create(name='vegetables')
        self.advert = models.Advert.objects.create(
            user=self.user,
            category=self.category,
            title='Potato',
            price='100.00',
        )
        self.data = dict(
            advert=self.advert,
            region='region',
            city='city',
            street='street',
            number='0',
        )

    def test_advert_field_is_required(self):
        del self.data['advert']
        with self.assertRaisesRegex(IntegrityError, r'NOT NULL'):
            self.model_class.objects.create(**self.data)

    def test_string_representation_returns_user(self):
        address = self.model_class.objects.create(**self.data)
        self.assertEqual(str(address), str(self.advert))


temp_media = settings.BASE_DIR / 'temp_media/'


@override_settings(MEDIA_ROOT=temp_media)
class AdvertImageModelTest(TransactionTestCase):
    def setUp(self) -> None:
        self.model_class = models.AdvertImage
        self.user = get_user_model().objects.create_user(email='test@test.com', password='qwe123!@#')
        self.category = models.Category.objects.create(name='vegetables')
        self.advert = models.Advert.objects.create(
            user=self.user,
            category=self.category,
            title='Potato',
            price='100.00',
        )
        self.data = dict(
            advert=self.advert,
            origin=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            order_num=0,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(temp_media, ignore_errors=True)

    def test_advert_field_is_required(self):
        del self.data['advert']
        with self.assertRaisesRegex(IntegrityError, r'NOT NULL'):
            self.model_class.objects.create(**self.data)

    def test_origin_field_is_required(self):
        del self.data['origin']
        with self.assertRaisesRegex(ValidationError, r'This field cannot be blank'):
            img = self.model_class.objects.create(**self.data)
            img.full_clean()

    def test_order_num_field_is_required(self):
        img = self.model_class.objects.create(**self.data)
        with self.assertRaisesRegex(IntegrityError, r'NOT NULL'):
            img.order_num = None
            img.save()

    def test_order_num_field_must_be_unique_for_one_advert(self):
        self.model_class.objects.create(**self.data)
        with self.assertRaisesRegex(IntegrityError, r'UNIQUE'):
            self.model_class.objects.create(**self.data)

    def test_order_num_field_must_not_be_unique_for_different_advert(self):
        another_advert = models.Advert.objects.create(
            user=self.user,
            category=self.category,
            title='carrot',
            price='100.00',
        )
        self.model_class.objects.create(**self.data)

        self.data['advert'] = another_advert
        self.model_class.objects.create(**self.data)  # not raise

    def test_string_representation_is_correct_format(self):
        expected_value = f'Image[0] of {self.advert.title}'
        img = self.model_class.objects.create(**self.data)

        self.assertEqual(str(img), expected_value)


class AdvertModelTest(TestCase):
    def setUp(self) -> None:
        self.model_class = models.Advert
        self.address_model_class = models.AdvertAddress
        self.user = get_user_model().objects.create_user(email='test@test.com', password='qwe123!@#')
        self.category = models.Category.objects.create(name='vegetables')
        self.data = dict(
            user=self.user,
            category=self.category,
            title='Potato',
            price='100.00',
        )

    def test_user_is_required(self):
        del self.data['user']
        with self.assertRaisesRegex(IntegrityError, r'NOT NULL'):
            self.model_class.objects.create(**self.data)

    def test_category_is_required(self):
        del self.data['category']
        with self.assertRaisesRegex(IntegrityError, r'NOT NULL'):
            self.model_class.objects.create(**self.data)

    def test_title_field_is_required(self):
        del self.data['title']
        advert = self.model_class.objects.create(**self.data)
        with self.assertRaisesRegex(ValidationError, r'This field cannot be blank.'):
            advert.full_clean()

    def test_title_field_is_unique_for_date(self):
        advert = self.model_class.objects.create(**self.data)
        with self.assertRaisesRegex(ValidationError, r'Title must be unique for Created date.'):
            advert_ = self.model_class.objects.create(**self.data)
            advert_.full_clean()

        advert.created_at = now() - timedelta(days=1)
        advert.save()

        self.model_class.objects.create(**self.data)  # not raise

    def test_price_field_is_required(self):
        del self.data['price']
        with self.assertRaisesRegex(IntegrityError, r'NOT NULL'):
            self.model_class.objects.create(**self.data)

    def test_price_field_cannot_be_less_0(self):
        self.data['price'] = -1
        with self.assertRaisesRegex(IntegrityError, r'CHECK'):
            self.model_class.objects.create(**self.data)

    def test_price_field_can_be_equal_0(self):
        self.data['price'] = 0
        advert = self.model_class.objects.create(**self.data)
        advert.full_clean()  # not raise

    def test_descr_field_is_optional(self):
        advert = self.model_class.objects.create(**self.data)
        advert.full_clean()  # not raise
        self.assertIsNone(advert.descr)

    def test_grades_field_is_expected_dict_by_default(self):
        expected_dict = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        advert = self.model_class.objects.create(**self.data)

        self.assertDictEqual(advert.grades, expected_dict)

    def test_use_pickup_field_is_false_by_default(self):
        advert = self.model_class.objects.create(**self.data)
        self.assertFalse(advert.use_pickup)

    def test_use_nova_post_field_is_false_by_default(self):
        advert = self.model_class.objects.create(**self.data)
        self.assertFalse(advert.use_nova_post)

    def test_use_courier_field_is_true_by_default(self):
        advert = self.model_class.objects.create(**self.data)
        self.assertTrue(advert.use_courier)

    def test_model_cannot_have_false_for_all_use_fields(self):
        self.data.update(dict(use_pickup=False, use_nova_post=False, use_courier=False))
        advert = self.model_class.objects.create(**self.data)
        with self.assertRaisesRegex(
            ValidationError, r'One of next field must be true: use_pickup, use_nova_post, use_courier.'
        ):
            advert.full_clean()

    # def test_address_field_cannot_be_empty_if_use_pickup_is_true(self):
    #     self.data.update(dict(use_pickup=True, use_nova_post=False, use_courier=False))
    #     advert = self.model_class.objects.create(**self.data)
    #     with self.assertRaisesRegex(ValidationError, r'Address must be specified if use_pickup field is true.'):
    #         advert.full_clean()

    def test_is_disabled_field_is_true_by_default(self):
        advert = self.model_class.objects.create(**self.data)
        self.assertTrue(advert.is_displayed)

    def test_string_representation_is_title(self):
        advert = self.model_class.objects.create(**self.data)
        self.assertEqual(str(advert), advert.title)

    def test_grade_property_returns_correct_grade(self):
        grades = {'1': 1, '2': 1, '3': 1, '4': 1, '5': 1}
        advert = self.model_class.objects.create(**self.data, grades=grades)

        self.assertEqual(advert.grade, 3)


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

    def test_string_representation_returns_name(self):
        category = self.models_class.objects.create(**self.data)
        self.assertEqual(str(category), category.name)
