from typing import Literal, Sequence

from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase, APIRequestFactory


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
