from typing import Any

from django.db.models import Model
from rest_framework.test import APITestCase

from accounts.models import User
from catalogs.models import Category
from catalogs.models.models import Advert
from utils.models import Address


class BaseTestCase(APITestCase):
    ############
    # Creators #
    ############
    TEST_EMAIL = 'rick.sanchez@test.com'
    TEST_PASSWORD = 'rick123!@#'
    TEST_PHONE = '+38 (012) 345 6789'
    TEST_FULL_NAME = 'Rick Sanchez'

    @staticmethod
    def create_test_user(email=TEST_EMAIL, password=TEST_PASSWORD, **extra_fields) -> User:
        return User.objects.create_user(email, password, **extra_fields)

    @staticmethod
    def create_test_address(content_obj, city='city', street='street', number='0', **extra_fields) -> Address:
        return Address.objects.create(content_obj=content_obj, city=city, street=street, number=number, **extra_fields)

    @staticmethod
    def create_test_category(name='name', **extra_fields) -> Category:
        return Category.objects.create(name=name, **extra_fields)

    def create_test_advert(
        self, owner: User, category: Category, name='name', price='100.00', **extra_fields
    ) -> Advert:
        return Advert.objects.create(owner=owner, category=category, name=name, price=price, **extra_fields)

    ###########
    # Asserts #
    ###########
    def assert_is_subclass(self, __cls, __class_or_tuple):
        self.assertTrue(issubclass(__cls, __class_or_tuple), msg=f'{__cls} is not subclass of {__class_or_tuple}.')

    def assert_model_instance(self, model_instance: Model, expected_data: dict[str, Any], equal=True):
        assert_methods = {True: self.assertEqual, False: self.assertNotEqual}
        for field_name, value in expected_data.items():
            got_field_value = getattr(model_instance, field_name)
            if isinstance(value, int) and isinstance(got_field_value, Model):
                got_field_value = got_field_value.id
            assert_methods[equal](
                got_field_value,
                value,
            )
