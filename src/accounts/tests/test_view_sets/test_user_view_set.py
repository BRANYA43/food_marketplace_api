from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from accounts.tests import APITestCase

from accounts import services

User = get_user_model()


class RefreshViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-refresh')
        self.user = self.create_test_user()
        self.refresh_token = self.user.refresh_token
        self.data = {'refresh': str(self.refresh_token)}

    def test_view_allows_only_post_method(self):
        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

        self.assert_not_allowed_methods(['get', 'put', 'patch', 'delete'], self.url)

    def test_view_is_accessed_for_unauthenticated_user(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_accessed_for_authenticated_user(self):
        self.login_user_by_token(self.user)
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_refreshes_valid_refresh_token(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_view_doesnt_refresh_invalid_refresh_token(self):
        self.data['refresh'] = 'invalid_token' + self.data['refresh']
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Token is invalid or expired')


class LogoutViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-logout')
        self.user = self.create_test_user()
        self.login_user_by_token(self.user)
        self.refresh_token = self.user.refresh_token
        self.data = {'refresh': str(self.refresh_token)}

    def test_view_allows_only_post_method(self):
        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

        self.assert_not_allowed_methods(['get', 'put', 'patch', 'delete'], self.url)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user, clear_auth_header=True)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_permission_error(response, 'Authentication credentials were not provided.')

    def test_view_is_accessed_for_authenticated_user(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_logs_user_out_with_valid_refresh_token(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)

        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Token is blacklisted')

    def test_view_logs_user_out_with_invalid_refresh_token(self):
        self.data['refresh'] = 'invalid_token' + self.data['refresh']
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Token is invalid or expired')


class LoginViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-login')
        self.user = self.create_test_user()
        self.data = {
            'email': self.TEST_EMAIL,
            'password': self.TEST_PASSWORD,
        }

    def test_view_allows_only_post_method(self):
        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

        self.assert_not_allowed_methods(['get', 'put', 'patch', 'delete'], self.url)

    def test_view_is_accessed_for_unauthenticated_user(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_isnt_accessed_for_authenticated_user(self):
        self.login_user_by_token(self.user)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_403_FORBIDDEN)
        self.assert_response_permission_error(response, 'User is already authenticated.')

    def test_view_logs_user_in_with_valid_credentials(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_view_doesnt_log_user_in_with_invalid_credentials(self):
        invalid_data = {'email': 'invalid.email@test.com', 'password': 'invalid_password'}
        response = self.client.post(self.url, invalid_data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)


class RegisterViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-register')
        self.data = {
            'email': self.TEST_EMAIL,
            'password': self.TEST_PASSWORD,
            'phone': '+380123456789',
        }

    def test_view_allows_only_post_method(self):
        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_201_CREATED)

        self.assert_not_allowed_methods(['get', 'put', 'patch', 'delete'], self.url)

    def test_view_is_accessed_for_unauthenticated_user(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_201_CREATED)

    def test_view_isnt_accessed_for_authenticated_user(self):
        del self.data['phone']
        user = self.create_test_user(**self.data)
        self.login_user_by_token(user)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_403_FORBIDDEN)
        self.assert_response_permission_error(response, 'User is already authenticated.')

    def test_view_register_user_with_valid_credentials(self):
        self.assertEqual(User.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.first()

        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertEqual(user.phone, services.normalize_phone_to_ukrainian_format(self.data['phone']))

    def test_view_doesnt_register_user_with_invalid_credentials(self):
        invalid_data = {
            'email': 'email.com',
            'password': 'qwe',
            'phone': '3324',
        }

        self.assertEqual(User.objects.count(), 0)

        response = self.client.post(self.url, invalid_data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

        errors = response.data.get('errors')

        self.assertIsNotNone(errors)
        self.assertIn('email', errors)
        self.assertIn('password', errors)
        self.assertIn('phone', errors)

    def test_view_doesnt_register_existed_user(self):
        del self.data['phone']
        User.objects.create_user(**self.data)

        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
