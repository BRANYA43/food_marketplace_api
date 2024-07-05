from datetime import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from utils.tests import APITestCase

from accounts import services, serializers, models

User = get_user_model()


class SetPasswordMeViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-set-password-me')
        self.user = self.create_test_user()
        self.login_user_by_token(self.user)

        self.data = dict(
            password=self.TEST_PASSWORD,
            new_password='new_password123!@#',
        )

    def test_view_allows_only_put_method(self):
        self.assert_not_allowed_methods(['get', 'post', 'patch', 'delete'], self.url)

        response = self.client.put(self.url, self.data)

        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.put(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='not_authenticated',
            detail='Authentication credentials were not provided.',
        )

    def test_view_isnt_accessed_for_authenticated_user_but_expired_access_token(self):
        self.login_user_by_token(self.user, use_expired_token=True)
        response = self.client.put(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='token_not_valid',
            detail='Given token not valid for any token type',
        )

    def test_view_is_accessed_for_authenticated_user(self):
        response = self.client.put(self.url, self.data)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_updates_user_password(self):
        response = self.client.put(self.url, self.data)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password(self.data['new_password']))

    def test_view_doesnt_returns_data(self):
        response = self.client.put(self.url, self.data)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

        self.assertFalse(response.data)


class DisableMeViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-disable-me')
        self.user = self.create_test_user(**self.rick_data)
        self.login_user_by_token(self.user)

    def test_view_allows_only_delete_method(self):
        self.assert_not_allowed_methods(['get', 'post', 'put', 'patch'], self.url)

        response = self.client.delete(self.url)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.delete(self.url)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='not_authenticated',
            detail='Authentication credentials were not provided.',
        )

    def test_view_isnt_accessed_for_authenticated_user_but_expired_access_token(self):
        self.login_user_by_token(self.user, use_expired_token=True)
        response = self.client.delete(self.url)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='token_not_valid',
            detail='Given token not valid for any token type',
        )

    def test_view_is_accessed_for_authenticated_user(self):
        response = self.client.delete(self.url)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response.data)

    def test_view_disables_current_user_without_address(self):
        response = self.client.delete(self.url)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.email, f'disabled.user.{self.user.id}@email.com')
        self.assertIsNone(self.user.full_name)
        self.assertIsNone(self.user.phone)
        self.assertIsNone(getattr(self.user, 'address', None))

    def test_view_disables_current_user_with_address(self):
        models.UserAddress.objects.create(
            user=self.user,
            region='region',
            city='city',
            street='street',
            number='0',
        )
        self.user.refresh_from_db()

        response = self.client.delete(self.url)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.email, f'disabled.user.{self.user.id}@email.com')
        self.assertIsNone(self.user.full_name)
        self.assertIsNone(self.user.phone)
        self.assertEqual(self.user.address.street, '-')
        self.assertEqual(self.user.address.number, '-')

    def test_view_blacklists_tokens_of_current_user(self):
        _ = [self.user.refresh_token for _ in range(3)]

        response = self.client.delete(self.url)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

        tokens = OutstandingToken.objects.filter(user=self.user)
        for token in tokens:
            self.assertTrue(
                BlacklistedToken.objects.filter(token=token).exists(),
                msg=f'Not blacklisted token: {token}',
            )

    def test_view_doesnt_disable_current_superuser_account(self):
        superuser = self.create_test_user(is_superuser=True)
        self.login_user_by_token(superuser)

        response = self.client.delete(self.url)

        self.assert_response_status(response, status.HTTP_403_FORBIDDEN)
        self.assert_response_client_error(
            response,
            code='permission_denied',
            detail='Superuser cannot be disabled.',
        )

    def test_view_doesnt_disable_tokens_of_current_superuser(self):
        superuser = self.create_test_user(is_superuser=True)
        self.login_user_by_token(superuser)

        response = self.client.delete(self.url)

        self.assert_response_status(response, status.HTTP_403_FORBIDDEN)
        self.assertEqual(BlacklistedToken.objects.count(), 0)

    def test_view_doesnt_disable_disabled_current_user(self):
        disabled_user = self.create_test_user(is_active=False)
        self.login_user_by_token(disabled_user)

        response = self.client.delete(self.url)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='authentication_failed',
            detail='User is inactive',
        )


class UpdateMeViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-update-me')
        self.serializer_class = serializers.UserProfileSerializer
        self.user = self.create_test_user(**self.rick_data)
        self.login_user_by_token(self.user)
        self.data = self.morty_data

    def test_view_allows_only_put_and_patch_methods(self):
        self.assert_not_allowed_methods(['get', 'post', 'delete'], self.url)

        response = self.client.put(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

        response = self.client.patch(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.put(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='not_authenticated',
            detail='Authentication credentials were not provided.',
        )

    def test_view_isnt_accessed_for_authenticated_user_but_expired_access_token(self):
        self.login_user_by_token(self.user, use_expired_token=True)
        response = self.client.put(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='token_not_valid',
            detail='Given token not valid for any token type',
        )

    def test_view_is_accessed_for_authenticated_user_who_own_current_account(self):
        response = self.client.put(self.url, self.data)
        self.user.refresh_from_db()
        expected_data = self.serializer_class(instance=self.user).data

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_data)

    def test_view_updates_user_with_valid_data(self):
        self.assertNotEqual(self.user.email, self.data['email'])
        self.assertNotEqual(self.user.phone, self.data['phone'])
        self.assertNotEqual(self.user.full_name, self.data['full_name'])

        response = self.client.put(self.url, self.data)
        self.user.refresh_from_db()

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertEqual(self.user.email, self.data['email'])
        self.assertEqual(self.user.phone, self.data['phone'])
        self.assertEqual(self.user.full_name, self.data['full_name'])

    def test_view_doesnt_update_with_invalid_data(self):
        invalid_data = {
            'full_name': 'q',
        }

        self.assertNotEqual(self.user, invalid_data['full_name'])

        response = self.client.put(self.url, invalid_data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user, invalid_data['full_name'])


class RetrieveMeViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-retrieve-me')
        self.user = self.create_test_user()
        self.login_user_by_token(self.user)

    def test_view_allowed_only_get_method(self):
        response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_200_OK)

        self.assert_not_allowed_methods(['post', 'put', 'patch', 'delete'], self.url)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response: Response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='not_authenticated',
            detail='Authentication credentials were not provided.',
        )

    def test_view_isnt_accessed_for_authenticated_user_with_expired_access_token(self):
        self.login_user_by_token(self.user, use_expired_token=True)
        response = self.client.get(self.url)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='token_not_valid',
            detail='Given token not valid for any token type',
        )

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
        self.assert_not_allowed_methods(['get', 'put', 'patch', 'delete'], self.url)

        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_accessed_for_unauthenticated_user(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertTrue(response.data.get('access'))

    def test_view_is_accessed_for_authenticated_user(self):
        self.login_user_by_token(self.user)
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertTrue(response.data.get('access'))

    def test_view_doesnt_refresh_invalid_refresh_token(self):
        self.data['refresh'] = 'invalid_token'
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            'token_not_valid',
            'Token is invalid or expired',
        )

    def test_view_doesnt_refresh_expired_refresh_token(self):
        self.refresh_token.set_exp(from_time=datetime.now() - jwt_api_settings.REFRESH_TOKEN_LIFETIME)
        self.data['refresh'] = str(self.refresh_token)
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            'token_not_valid',
            'Token is invalid or expired',
        )

    def test_view_doesnt_refresh_blacklisted_refresh_token(self):
        self.logout_user_by_token(self.user)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            'token_not_valid',
            'Token is blacklisted',
        )

    def test_view_doesnt_refresh_token_with_empty_data(self):
        response = self.client.post(self.url, {})
        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)


class LogoutViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-logout')
        self.user = self.create_test_user()
        self.login_user_by_token(self.user)
        self.refresh_token = self.user.refresh_token
        self.data = {'refresh': str(self.refresh_token)}

    def test_view_allows_only_post_method(self):
        self.assert_not_allowed_methods(['get', 'put', 'patch', 'delete'], self.url)

        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='not_authenticated',
            detail='Authentication credentials were not provided.',
        )

    def test_view_isnt_accessed_for_authenticated_user_with_expired_access_token(self):
        self.login_user_by_token(self.user, use_expired_token=True)
        response = self.client.get(self.url)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='token_not_valid',
            detail='Given token not valid for any token type',
        )

    def test_view_is_accessed_for_authenticated_user(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response.data)

    def test_view_logs_user_out_with_valid_refresh_token(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='token_not_valid',
            detail='Token is blacklisted',
        )

    def test_view_logs_user_out_with_invalid_refresh_token(self):
        self.data['refresh'] = 'invalid_token'
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            code='token_not_valid',
            detail='Token is invalid or expired',
        )

    def test_view_doesnt_log_user_out_with_empty_data(self):
        response = self.client.post(self.url, {})
        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)


class LoginViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-login')
        self.user = self.create_test_user()
        self.data = {
            'email': self.TEST_EMAIL,
            'password': self.TEST_PASSWORD,
        }

    def test_view_allows_only_post_method(self):
        self.assert_not_allowed_methods(['get', 'put', 'patch', 'delete'], self.url)

        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_accessed_for_unauthenticated_user(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertTrue(response.data.get('access'))
        self.assertTrue(response.data.get('refresh'))

    def test_view_isnt_accessed_for_authenticated_user(self):
        self.login_user_by_token(self.user)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_403_FORBIDDEN)
        self.assert_response_client_error(response, 'permission_denied', 'User is already authenticated.')

    def test_view_doesnt_log_user_in_with_invalid_credentials(self):
        invalid_data = {'email': 'invalid.email@test.com', 'password': 'invalid_password'}
        response = self.client.post(self.url, invalid_data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_client_error(
            response,
            'no_active_account',
            'No active account found with the given credentials',
        )

    def test_view_doesnt_log_user_in_with_empty_credentials(self):
        response = self.client.post(self.url, {})

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)


class RegisterViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-register')
        self.data = self.rick_data

    def test_view_allows_only_post_method(self):
        self.assert_not_allowed_methods(['get', 'put', 'patch', 'delete'], self.url)

        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_201_CREATED)

    def test_view_is_accessed_for_unauthenticated_user(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_201_CREATED)
        self.assertIsNone(response.data)

    def test_view_isnt_accessed_for_authenticated_user(self):
        user = self.create_test_user(**self.data)
        self.login_user_by_token(user)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_403_FORBIDDEN)
        self.assert_response_client_error(
            response,
            'permission_denied',
            'User is already authenticated.',
        )

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
            'full_name': 'qw',
        }

        self.assertEqual(User.objects.count(), 0)

        response = self.client.post(self.url, invalid_data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_view_doesnt_register_with_data_of_existed_user(self):
        del self.data['phone']
        User.objects.create_user(**self.data)

        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assert_response_client_error(
            response,
            'unique',
            'user with this email already exists.',
        )

    def test_view_doesnt_register_user_with_empty_data(self):
        self.assertEqual(User.objects.count(), 0)

        response = self.client.post(self.url, {})

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
