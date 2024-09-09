# mypy: disable-error-code="attr-defined"


from typing import Any, Literal

from rest_framework.fields import empty
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from utils.tests.cases import BaseTestCase


class ViewTestCase(BaseTestCase):
    def login_user_by_token(self, user):
        token = user.access_token
        credentials = {jwt_api_settings.AUTH_HEADER_NAME: f'{jwt_api_settings.AUTH_HEADER_TYPES[0]} {token}'}
        self.client.credentials(**credentials)

    def logout_user_by_token(self, user: User):
        tokens = OutstandingToken.objects.filter(user=user)

        for token in tokens:
            try:
                RefreshToken(token.token).blacklist()
            except TokenError:
                pass

        self.client.credentials()

    def assert_response(
        self,
        response: Response,
        status_code: int,
        output_data: list[dict[str, Any]] | dict[str, Any] | None = empty,
        used_paginate=False,
    ):
        self.assertEqual(
            response.status_code,
            status_code,
            msg=f'Expected the response status code "{status_code}", but got "{response.status_code}".',
        )

        if output_data is not empty:
            response_data = response.data['results'] if used_paginate else response.data
            self.assertEqual(response_data, output_data)

    def assert_http_methods_availability(
        self,
        url: str,
        methods: list[Literal['get', 'post', 'put', 'patch', 'delete']],
        status_code: int,
        input_data: dict[str, Any] | list[dict[str, Any]] = None,  # type: ignore
    ):
        for method in methods:
            response = getattr(self.client, method)(url, input_data)
            self.assert_response(response, status_code)
