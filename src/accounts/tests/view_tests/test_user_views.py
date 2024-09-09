from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from accounts.serializers import UserUpdateSerializer, UserRetrieveSerializer
from utils.models import Address
from utils.tests.cases import BaseTestCase

User = get_user_model()


class UserSetPasswordViewTest(BaseTestCase):
    url = reverse('user-set-password-me')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.input_data = dict(
            password=self.TEST_PASSWORD,
            new_password='new_password123!@#',
        )
        self.login_user_by_token(self.user)

    def test_view_allows_only_put_method(self):
        self.assert_http_methods_availability(
            self.url,
            ['get', 'post', 'patch', 'delete'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assert_http_methods_availability(
            self.url,
            ['put'],
            status.HTTP_204_NO_CONTENT,
            self.input_data,
        )

    def test_view_isnt_available_to_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.put(self.url, self.input_data)
        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_available_to_authenticated_user(self):
        response = self.client.put(self.url, self.input_data)
        self.assert_response(response, status.HTTP_204_NO_CONTENT)

    def test_view_sets_new_password(self):
        self.assertFalse(self.user.check_password(self.input_data['new_password']))

        self.client.put(self.url, self.input_data)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password(self.input_data['new_password']))

    def test_view_doesnt_set_new_password_if_user_uses_not_own_password(self):
        self.input_data['password'] = 'invalid_password'

        self.assertFalse(self.user.check_password(self.input_data['new_password']))

        self.client.put(self.url, self.input_data)

        self.user.refresh_from_db()

        self.assertFalse(self.user.check_password(self.input_data['new_password']))

    def test_view_doesnt_set_new_password_if_user_enters_invalid_new_password(self):
        self.input_data['new_password'] = '123'

        self.assertFalse(self.user.check_password(self.input_data['new_password']))

        self.client.put(self.url, self.input_data)

        self.user.refresh_from_db()

        self.assertFalse(self.user.check_password(self.input_data['new_password']))

    def test_view_returns_no_data(self):
        response = self.client.put(self.url, self.input_data)
        self.assert_response(response, status_code=status.HTTP_204_NO_CONTENT, expected_data=None)


class UserRetrieveViewTest(BaseTestCase):
    url = reverse('user-retrieve-me')
    serializer_class = UserRetrieveSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user(full_name=self.TEST_FULL_NAME, phone=self.TEST_PHONE)
        self.login_user_by_token(self.user)

    def test_view_allows_only_get_method(self):
        self.assert_http_methods_availability(
            self.url,
            ['post', 'put', 'patch', 'delete'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assert_http_methods_availability(self.url, ['get'], status.HTTP_200_OK)

    def test_view_isnt_available_to_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.get(self.url)
        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_isnt_available_to_authenticated_user(self):
        response = self.client.get(self.url)
        self.assert_response(response, status.HTTP_200_OK)

    def test_view_returns_data_without_address(self):
        serializer = self.create_serializer(self.serializer_class, instance=self.user)
        response = self.client.get(self.url)
        self.assert_response(
            response,
            status.HTTP_200_OK,
            expected_data=serializer.data,
        )

    def test_view_returns_data_with_address(self):
        self.create_test_address(self.user)
        self.user.refresh_from_db()
        serializer = self.create_serializer(self.serializer_class, instance=self.user)

        response = self.client.get(self.url)
        self.assert_response(
            response,
            status.HTTP_200_OK,
            expected_data=serializer.data,
        )


class UserDisableViewTest(BaseTestCase):
    url = reverse('user-disable-me')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.input_data = dict(password=self.TEST_PASSWORD)

        self.login_user_by_token(self.user)

    def test_view_allows_only_post_method(self):
        self.assert_http_methods_availability(
            self.url,
            ['get', 'put', 'patch', 'delete'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assert_http_methods_availability(
            self.url,
            ['post'],
            status.HTTP_204_NO_CONTENT,
            self.input_data,
        )

    def test_view_isnt_available_to_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_available_to_authenticated_user(self):
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_204_NO_CONTENT)

    def test_view_disable_user(self):
        address = self.create_test_address(self.user)

        self.client.post(self.url, self.input_data)

        self.user.refresh_from_db()
        address.refresh_from_db()

        self.assert_model_instance(
            self.user,
            dict(
                is_active=False,
                email=f'user.{self.user.pk}@disabled.com',
                full_name=f'disabled user {self.user.pk}',
                phone='+38 (012) 345 6789',
                password='-',
            ),
        )
        self.assert_model_instance(address, dict(number='-'))

    def test_view_returns_no_data(self):
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_204_NO_CONTENT, expected_data=None)


class UserUpdateViewTest(BaseTestCase):
    url = reverse('user-update-me')
    serializer_class = UserUpdateSerializer
    user_model = User
    address_model = Address

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.input_data: dict = dict(full_name='new full name')
        self.address_input_data = dict(
            city='new city',
            street='new street',
            number='new number',
        )
        self.login_user_by_token(self.user)

    def test_view_allows_only_patch_method(self):
        self.assert_http_methods_availability(
            self.url,
            ['get', 'post', 'put', 'delete'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assert_http_methods_availability(self.url, ['patch'], status.HTTP_200_OK, self.input_data)

    def test_view_isnt_available_to_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.patch(self.url, self.input_data)
        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_available_to_authenticated_user(self):
        response = self.client.patch(self.url, self.input_data)
        self.assert_response(response, status.HTTP_200_OK)

    def test_view_updates_user_without_address(self):
        self.assertEqual(self.address_model.objects.count(), 0)
        self.assert_model_instance(self.user, self.input_data, equal=False)

        self.client.patch(self.url, self.input_data)
        self.user.refresh_from_db()

        self.assertEqual(self.address_model.objects.count(), 0)
        self.assert_model_instance(self.user, self.input_data)

    def test_view_updates_user_with_address(self):
        address = self.create_test_address(self.user)

        self.assert_model_instance(self.user, self.input_data, equal=False)
        self.assert_model_instance(address, self.address_input_data, equal=False)

        data = dict(**self.input_data, address=self.address_input_data)
        self.client.patch(self.url, data, format='json')
        self.user.refresh_from_db()
        address.refresh_from_db()

        self.assert_model_instance(self.user, self.input_data)
        self.assert_model_instance(address, self.address_input_data)

    def test_view_updates_user_and_creates_address(self):
        self.assertEqual(self.address_model.objects.count(), 0)
        self.assert_model_instance(self.user, self.input_data, equal=False)

        data = dict(**self.input_data, address=self.address_input_data)
        self.client.patch(self.url, data, format='json')
        self.user.refresh_from_db()
        address = self.user.address.first()

        self.assertEqual(self.address_model.objects.count(), 1)
        self.assert_model_instance(self.user, self.input_data)
        self.assert_model_instance(address, self.address_input_data)

    def test_view_returns_data_without_address(self):
        response = self.client.patch(self.url, self.input_data)
        self.user.refresh_from_db()
        serializer = self.create_serializer(self.serializer_class, instance=self.user)

        self.assert_response(
            response,
            status.HTTP_200_OK,
            expected_data=serializer.data,
        )

    def test_view_returns_data_with_address(self):
        self.create_test_address(self.user)
        self.user.refresh_from_db()

        data = dict(**self.input_data, address=self.address_input_data)
        response = self.client.patch(self.url, data, format='json')
        self.user.refresh_from_db()
        serializer = self.create_serializer(self.serializer_class, instance=self.user)

        self.assert_response(
            response,
            status.HTTP_200_OK,
            expected_data=serializer.data,
        )


class UserRegisterViewTest(BaseTestCase):
    url = reverse('user-register')
    model = User

    def setUp(self) -> None:
        self.input_data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            full_name=self.TEST_FULL_NAME,
            phone=self.TEST_PHONE,
        )

    def test_view_allows_only_post_method(self):
        self.assert_http_methods_availability(
            self.url,
            ['get', 'put', 'patch', 'delete'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assert_http_methods_availability(
            self.url,
            ['post'],
            status.HTTP_201_CREATED,
            self.input_data,
        )

    def test_view_is_available_to_unauthenticated_user(self):
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_201_CREATED)

    def test_view_creates_user(self):
        self.assertEqual(self.model.objects.count(), 0)

        response = self.client.post(self.url, self.input_data)

        self.assertEqual(self.model.objects.count(), 1)
        self.assert_response(response, status.HTTP_201_CREATED)

        user = self.model.objects.first()

        self.assertTrue(user.check_password(self.input_data.pop('password')))
        self.assert_model_instance(user, self.input_data)

    def test_view_doesnt_create_existed_user(self):
        self.create_test_user(**self.input_data)

        self.assertEqual(self.model.objects.count(), 1)

        response = self.client.post(self.url, self.input_data)

        self.assertEqual(self.model.objects.count(), 1)
        self.assert_response(response, status.HTTP_400_BAD_REQUEST)

    def test_view_doesnt_create_user_with_invalid_credentials(self):
        self.input_data['email'] = 'invalid_email'

        self.assertEqual(self.model.objects.count(), 0)

        response = self.client.post(self.url, self.input_data)

        self.assertEqual(self.model.objects.count(), 0)
        self.assert_response(response, status.HTTP_400_BAD_REQUEST)

    def test_view_doesnt_return_data(self):
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_201_CREATED, expected_data=None)


class UserLoginViewTest(BaseTestCase):
    url = reverse('user-login')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.input_data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
        )

    def test_view_allows_only_post_method(self):
        self.assert_http_methods_availability(
            self.url,
            ['get', 'put', 'patch', 'delete'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assert_http_methods_availability(
            self.url,
            ['post'],
            status.HTTP_200_OK,
            self.input_data,
        )

    def test_view_doesnt_logs_user_in_with_disabled_account(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(str(response.data), r'no_active_account')

    def test_view_returns_access_and_refresh_tokens(self):
        response = self.client.post(self.url, self.input_data)

        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class UserLogoutViewTest(BaseTestCase):
    url = reverse('user-logout')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.input_data = dict(refresh=str(self.user.refresh_token))
        self.login_user_by_token(self.user)

    def test_view_allows_only_post_method(self):
        self.assert_http_methods_availability(
            self.url,
            ['get', 'put', 'patch', 'delete'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assert_http_methods_availability(
            self.url,
            ['post'],
            status.HTTP_204_NO_CONTENT,
            self.input_data,
        )

    def test_view_isnt_available_to_unauthenticated_user(self):
        self.logout_user_by_token(self.user)
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_available_to_authenticated_user(self):
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_204_NO_CONTENT)

    def test_view_returns_no_data(self):
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_204_NO_CONTENT, expected_data=None)


class UserRefreshViewTest(BaseTestCase):
    url = reverse('user-refresh')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.input_data = dict(refresh=str(self.user.refresh_token))

    def test_view_allows_only_post_method(self):
        self.assert_http_methods_availability(
            self.url,
            ['get', 'put', 'patch', 'delete'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assert_http_methods_availability(
            self.url,
            ['post'],
            status.HTTP_200_OK,
            self.input_data,
        )

    def test_view_is_available_to_unauthenticated_user(self):
        self.login_user_by_token(self.user)
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_200_OK)


class UserVerifyViewTest(BaseTestCase):
    url = reverse('user-verify')

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.input_data = dict(token=str(self.user.access_token))

    def test_view_allows_only_post_method(self):
        self.assert_http_methods_availability(
            self.url,
            ['get', 'put', 'patch', 'delete'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assert_http_methods_availability(
            self.url,
            ['post'],
            status.HTTP_204_NO_CONTENT,
            self.input_data,
        )

    def test_view_is_available_to_unauthenticated_user(self):
        self.login_user_by_token(self.user)
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_204_NO_CONTENT)

    def test_view_returns_no_data(self):
        response = self.client.post(self.url, self.input_data)
        self.assert_response(response, status.HTTP_204_NO_CONTENT, expected_data=None)
