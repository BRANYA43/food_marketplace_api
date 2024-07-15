from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from utils.tests import ApiTestCase

User = get_user_model()


class UserRegisterViewTest(ApiTestCase):
    url = reverse('user-register')
    model = User

    def setUp(self) -> None:
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            full_name=self.TEST_FULL_NAME,
            phone=self.TEST_PHONE,
        )

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'post', status.HTTP_201_CREATED, self.data)
        self.assert_not_allowed_methods(self.url, ['get', 'put', 'patch', 'delete'])

    def test_view_is_accessed_for_unregister_user(self):
        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_201_CREATED)

    def test_view_creates_user(self):
        self.assertEqual(self.model.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.count(), 1)

        user = self.model.objects.first()

        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertEqual(user.full_name, self.data['full_name'])
        self.assertEqual(user.phone, self.data['phone'])

    def test_view_doesnt_create_existed_user(self):
        self.create_test_user(**self.data)

        self.assertEqual(self.model.objects.count(), 1)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.model.objects.count(), 1)

    def test_view_doesnt_create_user_by_invalid_credentials(self):
        self.data['email'] = 'invalid_email'

        self.assertEqual(self.model.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.model.objects.count(), 0)
        self.assertIn('email', response.data['errors'][0]['attr'])

    def test_view_doesnt_return_data(self):
        response = self.client.post(self.url, self.data)
        self.assertIsNone(response.data)


class UserLoginViewTest(ApiTestCase):
    url = reverse('user-login')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
        )

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'post', status.HTTP_200_OK, self.data)
        self.assert_not_allowed_methods(self.url, ['get', 'put', 'patch', 'delete'])

    def test_view_doesnt_logs_user_in_with_invalid_password(self):
        self.data['password'] = 'invalid_password'
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(str(response.data), r'no_active_account')

    def test_view_doesnt_logs_user_in_with_disabled_account(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(str(response.data), r'no_active_account')

    def test_view_returns_access_and_refresh_tokens(self):
        response = self.client.post(self.url, self.data)

        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class UserLogoutViewTest(ApiTestCase):
    url = reverse('user-logout')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(
            refresh=str(self.user.refresh_token),
        )

        self.login_user_by_token(self.user)

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'post', status.HTTP_204_NO_CONTENT, self.data)
        self.assert_not_allowed_methods(self.url, ['get', 'put', 'patch', 'delete'])

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(str(response.data), r'not_authenticated')

    def test_view_logs_user_out_with_expired_refresh_token(self):
        self.data['refresh'] = str(self.get_expired_token(self.user.refresh_token))
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(str(response.data), r'token_not_valid')
        self.assertRegex(str(response.data), r'Token is invalid or expired')

    def test_view_logs_user_out_by_same_refresh_token_twice(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(str(response.data), r'token_not_valid')
        self.assertRegex(str(response.data), r'Token is blacklisted')
