from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from accounts.serializers import UserUpdateSerializer
from utils.models import Address
from utils.tests import ApiTestCase

User = get_user_model()


class UserSetPasswordViewTest(ApiTestCase):
    url = reverse('user-set-password-me')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(
            password=self.TEST_PASSWORD,
            new_password='new_password123!@#',
        )
        self.login_user_by_token(self.user)

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'put', status.HTTP_204_NO_CONTENT, self.data)
        self.assert_not_allowed_methods(self.url, ['get', 'post', 'patch', 'delete'])

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.put(self.url, self.data)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_accessed_for_authenticated_user(self):
        response = self.client.put(self.url, self.data)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_sets_new_password(self):
        self.assertFalse(self.user.check_password(self.data['new_password']))

        self.client.put(self.url, self.data)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password(self.data['new_password']))

    def test_view_doesnt_set_new_password_if_user_uses_not_own_password(self):
        self.data['password'] = 'invalid_password'

        self.assertFalse(self.user.check_password(self.data['new_password']))

        self.client.put(self.url, self.data)

        self.user.refresh_from_db()

        self.assertFalse(self.user.check_password(self.data['new_password']))

    def test_view_doesnt_set_new_password_if_user_enters_invalid_new_password(self):
        self.data['new_password'] = '123'

        self.assertFalse(self.user.check_password(self.data['new_password']))

        self.client.put(self.url, self.data)

        self.user.refresh_from_db()

        self.assertFalse(self.user.check_password(self.data['new_password']))

    def test_view_returns_no_data(self):
        response = self.client.put(self.url, self.data)
        self.assertIsNone(response.data)


class UserDisableViewTest(ApiTestCase):
    url = reverse('user-disable-me')
    model = User
    address_model = Address

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(password=self.TEST_PASSWORD)

        self.login_user_by_token(self.user)

    def test_view_allows_only_post_method(self):
        self.assert_not_allowed_methods(self.url, ['get', 'post', 'put', 'patch'])
        self.assert_allowed_method(self.url, 'delete', status.HTTP_204_NO_CONTENT, self.data)

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.delete(self.url, self.data)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_accessed_for_authenticated_user(self):
        response = self.client.delete(self.url, self.data)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_disable_user(self):
        address = self.create_test_address(self.user)
        self.user.refresh_from_db()

        self.client.delete(self.url, self.data)

        self.user.refresh_from_db()

        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.email, f'user.{self.user.pk}@disabled.com')
        self.assertEqual(self.user.full_name, f'disabled user {self.user.pk}')
        self.assertEqual(self.user.phone, '+38 (012) 345 6789')
        self.assertEqual(self.user.password, '-')

        address.refresh_from_db()

        self.assertEqual(address.number, '-')

    def test_view_returns_no_data(self):
        response = self.client.delete(self.url, self.data)
        self.assertIsNone(response.data)


class UserUpdateViewTest(ApiTestCase):
    url = reverse('user-update-me')
    serializer_class = UserUpdateSerializer
    model = User
    address_model = Address

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data: dict = dict(
            full_name='new full name',
        )
        self.login_user_by_token(self.user)

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'patch', status.HTTP_200_OK, self.data)
        self.assert_not_allowed_methods(self.url, ['get', 'post', 'put', 'delete'])

    def test_view_isnt_accessed_for_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.patch(self.url, self.data)
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_accessed_for_authenticated_user(self):
        response = self.client.patch(self.url, self.data)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_updates_user_without_address(self):
        self.assertEqual(self.address_model.objects.count(), 0)
        self.assertNotEqual(self.user.full_name, self.data['full_name'])

        self.client.patch(self.url, self.data)

        self.assertEqual(self.address_model.objects.count(), 0)

        self.user.refresh_from_db()

        self.assertEqual(self.user.full_name, self.data['full_name'])

    def test_view_updates_user_with_address(self):
        self.data['address'] = dict(number='new_number')
        address = self.create_test_address(self.user)

        self.assertNotEqual(self.user.full_name, self.data['full_name'])
        self.assertNotEqual(address.number, self.data['address']['number'])

        self.client.patch(self.url, self.data, format='json')

        self.user.refresh_from_db()
        address.refresh_from_db()

        self.assertEqual(self.user.full_name, self.data['full_name'])
        self.assertEqual(address.number, self.data['address']['number'])

    def test_view_updates_user_and_creates_address(self):
        self.data['address'] = dict(
            city='city',
            street='street',
            number='number',
        )

        self.assertEqual(self.address_model.objects.count(), 0)
        self.assertNotEqual(self.user.full_name, self.data['full_name'])

        self.client.patch(self.url, self.data, format='json')

        self.assertEqual(self.address_model.objects.count(), 1)

        self.user.refresh_from_db()
        address = self.address_model.objects.first()

        self.assertEqual(self.user.full_name, self.data['full_name'])
        self.assertEqual(address.content_obj.id, self.user.id)
        self.assertEqual(address.city, self.data['address']['city'])
        self.assertEqual(address.street, self.data['address']['street'])
        self.assertEqual(address.number, self.data['address']['number'])

    def test_view_returns_expected_data_without_address(self):
        response = self.client.patch(self.url, self.data)

        self.user.refresh_from_db()
        serializer = self.serializer_class(self.user, self.data, partial=True)
        serializer.is_valid()
        expected_data = serializer.data

        self.assertDictEqual(response.data, expected_data)

    def test_view_returns_expected_data_with_address(self):
        self.create_test_address(self.user)
        self.user.refresh_from_db()

        response = self.client.patch(self.url, self.data, format='json')

        self.user.refresh_from_db()
        serializer = self.serializer_class(self.user, self.data, partial=True)
        serializer.is_valid()
        expected_data = serializer.data

        self.assertDictEqual(response.data, expected_data)


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

    def test_view_doesnt_create_user_with_invalid_credentials(self):
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

    def test_view_logs_user_out_with_same_refresh_token_twice(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(str(response.data), r'token_not_valid')
        self.assertRegex(str(response.data), r'Token is blacklisted')


class UserRefreshViewTest(ApiTestCase):
    url = reverse('user-refresh')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(
            refresh=str(self.user.access_token),
        )

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'post', status.HTTP_200_OK, self.data)
        self.assert_not_allowed_methods(self.url, ['get', 'put', 'patch', 'delete'])

    def test_view_is_accessed_for_user_with_expire_access_token(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_accessed_for_authenticated_user(self):
        self.login_user_by_token(self.user)
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_doesnt_refresh_tokens_for_expired_refresh_token(self):
        self.data['refresh'] = str(self.get_expired_token(self.user.refresh_token))
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(str(response.data), r'token_not_valid')
        self.assertRegex(str(response.data), r'Token is invalid or expired')

    def test_view_doesnt_refresh_token_for_blacklisted_refresh_token(self):
        self.login_user_by_token(self.user)
        self.logout_user_by_token(self.user)
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(str(response.data), r'token_not_valid')
        self.assertRegex(str(response.data), r'Token is blacklisted')


class UserVerifyViewTest(ApiTestCase):
    url = reverse('user-verify')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(token=str(self.user.access_token))

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'post', status.HTTP_204_NO_CONTENT, self.data)
        self.assert_not_allowed_methods(self.url, ['get', 'put', 'patch', 'delete'])

    def test_view_is_accessed_for_user_with_expire_access_token(self):
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_is_accessed_for_authenticated_user(self):
        self.login_user_by_token(self.user)
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_verifies_token(self):
        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_204_NO_CONTENT)

    def test_view_doesnt_verifies_expired_token(self):
        self.data['token'] = str(self.get_expired_token(self.user.access_token))
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(response.data['errors'][0]['detail'], 'Token is invalid or expired')

    def test_view_doesnt_verifies_broken_token(self):
        self.data['token'] += 'broken'
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(response.data['errors'][0]['detail'], 'Token is invalid or expired')

    def test_view_doesnt_verifies_blacklisted_token(self):
        token = self.user.refresh_token
        token.blacklist()
        self.data['token'] = str(token)
        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertRegex(response.data['errors'][0]['detail'], 'Token is blacklisted')

    def test_view_returns_no_data(self):
        response = self.client.post(self.url, self.data)

        self.assertIsNone(response.data)
