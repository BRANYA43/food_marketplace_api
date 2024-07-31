from typing import Literal, Sequence, Any

from django.core.exceptions import ValidationError as django_ValidationError
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError as rest_ValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from catalogs.models import Category
from utils.models import Address


class ApiTestCase(APITestCase):
    request_factory = APIRequestFactory()
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

    def get_expired_token(self, token):
        token.set_exp(from_time=now() - jwt_api_settings.REFRESH_TOKEN_LIFETIME)
        return token

    def login_user_by_token(self, user, use_expired_token=False):
        token = user.access_token

        if use_expired_token:
            token = self.get_expired_token(token)

        credentials = {jwt_api_settings.AUTH_HEADER_NAME: f'{jwt_api_settings.AUTH_HEADER_TYPES[0]} {token}'}
        self.client.credentials(**credentials)

    def logout_user_by_token(self, user, clear_auth_header=True):
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            RefreshToken(token.token).blacklist()

        if clear_auth_header:
            self.client.credentials()

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

    def assert_model_fields_max_length(self, model, data: dict[str, Any], fields: dict[str, Any]):
        for field, max_length in fields.items():
            copy_data = data.copy()

            # Check max_length without error
            copy_data[field] = 'a' * max_length
            try:
                model(**copy_data).full_clean()  # not raise error
            except django_ValidationError:
                raise AssertionError(
                    f'The field "{field}" has less max_length the than specified value "{max_length}".'
                )

            # Check max_length with error
            copy_data[field] += 'a'
            with self.assertRaisesRegex(
                django_ValidationError,
                rf'Ensure this value has at most {max_length} characters',
                msg=(
                    f'The field "{field}" has a greater max_length than the specified value "{max_length}", or the '
                    f'field class "{field}" is a TextField.'
                ),
            ):
                model(**copy_data).full_clean()

    def assert_write_only_serializer_fields(self, serializer_class, data: dict, fields: Sequence[str]):
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        for field in fields:
            self.assertIsNone(serializer.data.get(field), f'This field "{field}" is not write only.')

    def assert_required_serializer_fields(self, serializer_class, data: dict, fields: Sequence[str]):
        for field in fields:
            data = data.copy()
            del data[field]
            serializer = serializer_class(data=data)
            with self.assertRaisesRegex(
                rest_ValidationError, rf'{field}.+required', msg=f'This field "{field}" is not required.'
            ):
                serializer.is_valid(raise_exception=True)

    def assert_optional_serializer_fields(self, serializer_class, fields: Sequence[str]):
        serializer = serializer_class(data={})
        serializer.is_valid()
        for field in fields:
            self.assertIsNone(
                serializer.errors.get(field),
                f'This field "{field}" is not optional. It is required.',
            )
