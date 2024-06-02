from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase as RFAPITestCase

from core.settings.components.simple_jwt import SIMPLE_JWT


class APITestCase(RFAPITestCase):
    TEST_USER_MODEL = get_user_model()
    TEST_EMAIL = 'rick.sanchez@test.com'
    TEST_PASSWORD = 'qwr123!@#'

    def login_user_by_token(self, user):
        auth_header_name = SIMPLE_JWT['AUTH_HEADER_NAME']
        auth_header_type = SIMPLE_JWT['AUTH_HEADER_TYPES'][0]
        credentials = {auth_header_name: f'{auth_header_type} {user.access_token}'}
        self.client.credentials(**credentials)

    def create_test_user(self, email=TEST_EMAIL, password=TEST_PASSWORD, user_model=TEST_USER_MODEL, **extra_fields):
        return user_model.objects.create_user(email, password, **extra_fields)

    def assert_not_allowed_methods(self, methods: list[str], url: str):
        for method in methods:
            response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def assert_response_permission_error(self, response: Response, expected_msg: str, is_regex=False):
        data = response.data
        self.assertIn('detail', data)
        if is_regex:
            self.assertRegex(data['detail'], expected_msg)
        else:
            self.assertEqual(data['detail'], expected_msg)

    def assert_response_status(self, response: Response, status: int):
        self.assertEqual(response.status_code, status)
