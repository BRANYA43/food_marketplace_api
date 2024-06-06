from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken

from utils.tests import APITestCase

from accounts import services, permissions, serializers

User = get_user_model()


class DisableMeViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-disable-me')
        self.user = self.create_test_user()
        self.login_user_by_token(self.user)

    def test_view_allows_only_delete_method(self):
        self.assert_not_allowed_methods(['get', 'post', 'put', 'patch'], self.url)

        response = self.client.delete(self.url)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user, clear_auth_header=True)
        response = self.client.delete(self.url)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_accessed_for_authenticated_user_who_own_current_account(self):
        response = self.client.delete(self.url)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_disabled_account_of_current_user(self):
        response = self.client.delete(self.url)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class UpdateMeViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-update-me')
        self.serializer_class = serializers.UserProfileUpdateSerializer
        self.user = self.create_test_user()
        self.login_user_by_token(self.user)
        self.data = {
            'full_name': 'Rick Sanchez',
        }

    def test_view_allows_only_put_and_patch_methods(self):
        response = self.client.put(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

        response = self.client.patch(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

        self.assert_not_allowed_methods(['get', 'post', 'delete'], self.url)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user, clear_auth_header=True)
        response: Response = self.client.put(self.url, self.data)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_accessed_for_authenticated_user_who_own_current_account(self):
        expected_data = self.serializer_class(instance=self.user).data
        expected_data['full_name'] = self.data['full_name']
        response = self.client.put(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_data)

    def test_view_doesnt_update_with_invalid_data(self):
        self.data['full_name'] = 'qw'
        response = self.client.put(self.url, self.data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)


class MeViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-me')
        self.user = self.create_test_user()
        self.login_user_by_token(self.user)

    def test_view_allowed_only_get_method(self):
        response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_200_OK)

        self.assert_not_allowed_methods(['post', 'put', 'patch', 'delete'], self.url)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user, clear_auth_header=True)
        response: Response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_accessed_for_authenticated_user_who_own_current_account(self):
        expected_data = serializers.UserProfileSerializer(instance=self.user).data
        response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_200_OK)

        self.assertDictEqual(response.data, expected_data)


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
        self.assertEqual(response.data['errors'][0]['code'], InvalidToken.default_code)
        self.assertEqual(response.data['errors'][0]['detail'], InvalidToken.default_detail)


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
        self.assertEqual(response.data['errors'][0]['code'], NotAuthenticated.default_code)
        self.assertEqual(response.data['errors'][0]['detail'], NotAuthenticated.default_detail)

    def test_view_is_accessed_for_authenticated_user(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_logs_user_out_with_valid_refresh_token(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)

        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['errors'][0]['code'], InvalidToken.default_code)
        self.assertEqual(response.data['errors'][0]['detail'], 'Token is blacklisted')

    def test_view_logs_user_out_with_invalid_refresh_token(self):
        self.data['refresh'] = 'invalid_token' + self.data['refresh']
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['errors'][0]['code'], InvalidToken.default_code)
        self.assertEqual(response.data['errors'][0]['detail'], 'Token is invalid or expired')


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
        self.assertEqual(response.data['errors'][0]['code'], PermissionDenied.default_code)
        self.assertEqual(response.data['errors'][0]['detail'], permissions.IsUnauthenticated.message)

    def test_view_logs_user_in_with_valid_credentials(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_view_doesnt_log_user_in_with_invalid_credentials(self):
        invalid_data = {'email': 'invalid.email@test.com', 'password': 'invalid_password'}
        response = self.client.post(self.url, invalid_data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['errors'][0]['code'], 'no_active_account')
        self.assertEqual(response.data['errors'][0]['detail'], 'No active account found with the given credentials')


class RegisterViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-register')
        self.data = {
            'email': self.TEST_EMAIL,
            'password': self.TEST_PASSWORD,
            'phone': '+380123456789',
            'full_name': 'Rick Sanchez',
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
        self.assertEqual(response.data['errors'][0]['code'], 'permission_denied')
        self.assertEqual(response.data['errors'][0]['detail'], 'User is already authenticated.')

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

    def test_view_doesnt_register_existed_user(self):
        del self.data['phone']
        User.objects.create_user(**self.data)

        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['code'], 'unique')
        self.assertEqual(response.data['errors'][0]['detail'], 'user with this email already exists.')
