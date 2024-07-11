from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase as RFAPITestCase, APIRequestFactory
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from catalogs import models as catalog_models


class APITestCase(RFAPITestCase):
    request_factory = APIRequestFactory()
    TEST_USER_MODEL = get_user_model()
    TEST_EMAIL = 'test@test.com'
    TEST_PASSWORD = 'qwr123!@#'

    @property
    def rick_data(self) -> dict:
        return dict(
            email='rick.sanchez@test.com',
            password='rick123!@#',
            full_name='Rick Sanchez',
            phone='+38 (012) 345 6789',
        )

    @property
    def morty_data(self) -> dict:
        return dict(
            email='morty@test.com',
            password='morty123!@#',
            full_name='Morty',
            phone='+38 (098) 765 4321',
        )

    def login_user_by_token(self, user, use_expired_token=False):
        token = user.access_token

        if use_expired_token:
            token.set_exp(from_time=datetime.now() - jwt_api_settings.ACCESS_TOKEN_LIFETIME)

        credentials = {jwt_api_settings.AUTH_HEADER_NAME: f'{jwt_api_settings.AUTH_HEADER_TYPES[0]} {token}'}
        self.client.credentials(**credentials)

    def logout_user_by_token(self, user, clear_auth_header=True):
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            RefreshToken(token.token).blacklist()

        if clear_auth_header:
            self.client.credentials()

    def assert_not_allowed_methods(self, methods: list[str], url: str):
        for method in methods:
            response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def assert_response_status(self, response: Response, status: int):
        self.assertEqual(response.status_code, status)

    def assert_response_client_error(self, response: Response, code: str, detail: str = None):
        errors = response.data.get('errors')
        self.assertIsNotNone(errors)
        self.assertEqual(errors[0]['code'], code)
        if detail:
            self.assertEqual(errors[0]['detail'], detail)

    @staticmethod
    def create_test_user(email=TEST_EMAIL, password=TEST_PASSWORD, user_model=TEST_USER_MODEL, **extra_fields):
        return user_model.objects.create_user(email, password, **extra_fields)

    @staticmethod
    def create_test_user_address(
        user, region='Test Region', city='Test City', street='Test Street', number='0', **extra_fields
    ):
        return catalog_models.AdvertAddress.objects.create(
            user=user, region=region, city=city, street=street, number=number, **extra_fields
        )

    @staticmethod
    def create_test_category(name='Test Catalog', **extra_fields):
        return catalog_models.Category.objects.create(name=name, **extra_fields)

    @staticmethod
    def create_test_advert(user, catalog, title='Test Advert', price='1000', **extra_fields):
        return catalog_models.Advert.objects.create(
            user=user, catalog=catalog, title=title, price=price, **extra_fields
        )

    @staticmethod
    def create_test_advert_address(
        advert, region='Test Region', city='Test City', street='Test Street', number='0', **extra_fields
    ):
        return catalog_models.AdvertAddress.objects.create(
            advert=advert, region=region, city=city, street=street, number=number, **extra_fields
        )
