from typing import Any, Type

from django.db.models import Model
from rest_framework.fields import empty
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.test import APITestCase

from accounts.models import User
from catalogs.models import Category
from catalogs.models.models import Advert
from utils.models import Address


class BaseTestCase(APITestCase):
    ####################################################################################################################
    # Creators                                                                                                         #
    ####################################################################################################################
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

    @staticmethod
    def create_test_advert(owner: User, category: Category, name='name', price='100.00', **extra_fields) -> Advert:
        return Advert.objects.create(owner=owner, category=category, name=name, price=price, **extra_fields)

    @staticmethod
    def create_serializer_deprecated(
        serializer: Type[Serializer],
        input_data: dict[str, Any] | list[dict[str, Any]] = empty,
        save=False,
        **extra_params,
    ) -> Serializer | ModelSerializer:
        serializer = serializer(data=input_data, **extra_params)

        if input_data is not empty:
            serializer.is_valid(raise_exception=True)

        if save:
            serializer.save()

        return serializer

    @staticmethod
    def create_serializer(
        serializer_class: Type[Serializer],
        save=False,
        **serializer_args,
    ) -> Serializer | ModelSerializer:
        """
        Creates the serializer and passes to it args through `serializer_args`.

        Supply `data` to call `.is_valid()`.

        Set `save` to true to call `.save()`.
        """
        serializer = serializer_class(**serializer_args)

        if 'data' in serializer_args:
            serializer.is_valid(raise_exception=True)

        if save:
            serializer.save()

        return serializer

    ####################################################################################################################
    # Asserts                                                                                                          #
    ####################################################################################################################
    def assert_is_subclass(self, __cls, __class_or_tuple):
        """
        Checks that the class is the subclass of another class or classes.
        """
        self.assertTrue(issubclass(__cls, __class_or_tuple), msg=f'{__cls} is not subclass of {__class_or_tuple}.')

    def assert_model_instance(self, instance: Model, expected_data: dict[str, Any], equal=True):
        """
        Checks whether a model instance fields are equal to the expected data or not.

        :param instance: a model instance whose field values will be checked
        :param expected_data: a dict where keys are field names and values are expected field values.
        :param equal: if True method checks that field values are equal to values in the expected data.
        If False method checks that field values aren't equal to values in the expected data.
        """
        assert_methods = {True: self.assertEqual, False: self.assertNotEqual}
        for field_name, value in expected_data.items():
            got_field_value = getattr(instance, field_name)
            if isinstance(value, int) and isinstance(got_field_value, Model):
                got_field_value = got_field_value.id
            assert_methods[equal](
                got_field_value,
                value,
            )

    def assert_serializer_output_data(
        self,
        serializer_class: Type[Serializer],
        expected_data: dict[str, Any] | list[dict[str, Any]],
        save=False,
        **serializer_args,
    ):
        """
        Compares `expected_data` with `data` of created serializer.
        Creates the serializer and passes to it args through `serializer_args` before comparison.

        Supply `data` to call `.is_valid()`.

        Set `save` to true to call `.save()`.
        """
        serializer = self.create_serializer(serializer_class, save=save, **serializer_args)

        self.assertDictEqual(serializer.data, expected_data)
