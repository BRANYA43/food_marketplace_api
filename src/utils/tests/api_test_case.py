from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase as RFAPITestCase, APIRequestFactory

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken


class APITestCase(RFAPITestCase):
    request_factory = APIRequestFactory()
    TEST_USER_MODEL = get_user_model()
    TEST_EMAIL = 'test@test.com'
    TEST_PASSWORD = 'qwr123!@#'
    AUTH_HEADER_NAME = settings.SIMPLE_JWT['AUTH_HEADER_NAME']
    AUTH_HEADER_TYPES = settings.SIMPLE_JWT['AUTH_HEADER_TYPES']

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

    def login_user_by_token(self, user):
        credentials = {self.AUTH_HEADER_NAME: f'{self.AUTH_HEADER_TYPES[0]} {user.access_token}'}
        self.client.credentials(**credentials)

    def logout_user_by_token(self, user, clear_auth_header=True):
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            RefreshToken(token.token).blacklist()

        if clear_auth_header:
            self.client.credentials()

    def create_test_user(self, email=TEST_EMAIL, password=TEST_PASSWORD, user_model=TEST_USER_MODEL, **extra_fields):
        return user_model.objects.create_user(email, password, **extra_fields)

    def assert_not_allowed_methods(self, methods: list[str], url: str):
        for method in methods:
            response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def assert_response_status(self, response: Response, status: int):
        self.assertEqual(response.status_code, status)

    def assert_response_client_error(self, response: Response, code: str, detail: str = None):
        errors = response.data.get('errors')
        self.assertIsNotNone(errors)
        self.assertEqual(errors['code'], code)
        if detail:
            self.assertEqual(errors['detail'], detail)
