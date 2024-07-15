from typing import Literal, Sequence

from django.core.exceptions import ValidationError as django_ValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase, APIRequestFactory

from accounts.models import User
from utils.models import Address


class ApiTestCase(APITestCase):
    request_factory = APIRequestFactory()
    TEST_EMAIL = 'rick.sanchez@test.com'
    TEST_PASSWORD = 'rick123!@#'
    TEST_PHONE = '+38 (012) 345 6789'
    TEST_FULL_NAME = 'Rick Sanchez'

    def assert_is_subclass(self, __cls, __class_or_tuple):
        self.assertTrue(issubclass(__cls, __class_or_tuple), msg=f'{__cls} is not subclass of {__class_or_tuple}.')

    def assert_response_status(self, response: Response, status_code: int):
        self.assertEqual(
            response.status_code,
            status_code,
            msg=f'Expected response status code "{status_code}", but got "{response.status_code}".',
        )

    def assert_allowed_method(
        self, url, method: Literal['get', 'post', 'put', 'patch', 'delete'], status_code: int, data=None
    ):
        response = getattr(self.client, method)(url, data)
        self.assertNotEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            msg=f'Expected method "{method}" is not allowed.',
        )
        self.assert_response_status(response, status_code)

    def assert_not_allowed_methods(self, url: str, methods: Sequence[Literal['get', 'post', 'put', 'patch', 'delete']]):
        for method in methods:
            response = getattr(self.client, method)(url)
            self.assert_response_status(response, status.HTTP_405_METHOD_NOT_ALLOWED)

    def assert_validation_model_field(self, model, data: dict, detail: str):
        regex = rf'.*{detail}.*'
        with self.assertRaisesRegex(django_ValidationError, regex):
            instance = model(**data)
            instance.full_clean()

    @staticmethod
    def create_test_user(email=TEST_EMAIL, password=TEST_PASSWORD, **extra_fields) -> User:
        return User.objects.create_user(email, password, **extra_fields)

    @staticmethod
    def create_test_address(content_obj, region='region', city='city', street='street', number='0', **extra_fields):
        return Address.objects.create(
            content_obj=content_obj, region=region, city=city, street=street, number=number, **extra_fields
        )

    def assert_required_model_fields(self, model, data: dict, fields: Sequence[str]):
        for field in fields:
            data = data.copy()
            del data[field]
            instance = model(**data)
            with self.assertRaisesRegex(
                django_ValidationError, rf'{field}.+cannot be blank', msg=f'This field "{field}" is not required.'
            ):
                instance.full_clean()

    def assert_optional_model_fields(self, model, data: dict, fields: Sequence[str]):
        for field in fields:
            if field in data:
                data = data.copy()
                del data[field]
            instance = model(**data)
            try:
                instance.full_clean()
            except (django_ValidationError, IntegrityError):
                raise AssertionError(f'This field "{field}" is not optional. It is required.')
            else:
                self.assertIsNone(
                    getattr(instance, field),
                    msg=f'This field "{field}" is not optional. It is set by default.',
                )

    def assert_set_model_fields_by_default(self, model, data: dict, fields: dict):
        for field, value in fields.items():
            if field in data:
                data = data.copy()
                del data[field]
            instance = model(**data)
            try:
                instance.full_clean()
            except (django_ValidationError, IntegrityError):
                raise AssertionError(f'This field "{field}" have no a default value.')
            else:
                got_value = getattr(instance, field)
                self.assertEqual(
                    got_value,
                    value,
                    f'This field "{field}" is not set by default as "{value}". (There set {got_value}.)',
                )
