from typing import Literal, Sequence

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase, APIRequestFactory

from accounts.models import User


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

    def assert_required_model_field(self, model, field: str, data: dict, detail: str):
        del data[field]
        regex = rf'.*{detail}.*'
        with self.assertRaisesRegex(
            (ValidationError, IntegrityError),
            regex,
            msg=f'This field "{field}" is not required.',
        ):
            instance = model(**data)
            instance.full_clean()

    def assert_optional_model_field(self, model, field: str, data: dict):
        if field in data:
            del data[field]
        instance = model(**data)
        try:
            instance.full_clean()
        except (ValidationError, IntegrityError):
            raise AssertionError(f'This field "{field}" is not optional. It is required field.')
        self.assertIsNone(
            getattr(instance, field), msg=f'This field "{field}" is not optional. It has value by default.'
        )

    def assert_model_field_default_value(self, model, field: str, data: dict, expected_value):
        instance = model(**data)
        field_value = getattr(instance, field)
        if isinstance(expected_value, bool):
            if expected_value:
                self.assertTrue(field_value, msg='Expected default value "True", but got "False".')
            else:
                self.assertFalse(field_value, msg='Expected default value "False", but got "True".')
        else:
            self.assertEqual(
                field_value, expected_value, msg=f'Expected default value "{expected_value}", but got "{field_value}".'
            )

    def assert_validation_model_field(self, model, data: dict, detail: str):
        regex = rf'.*{detail}.*'
        with self.assertRaisesRegex(ValidationError, regex):
            instance = model(**data)
            instance.full_clean()

    @staticmethod
    def create_test_user(email=TEST_EMAIL, password=TEST_PASSWORD, **extra_fields) -> User:
        return User.objects.create_user(email, password, **extra_fields)
