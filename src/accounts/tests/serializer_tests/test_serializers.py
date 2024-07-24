from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import serializers, mixins
from accounts.serializers.serializers import UserDisableSerializer
from utils.serializers.mixins import AddressCreateUpdateMixin
from utils.tests import ApiTestCase

User = get_user_model()


class UserRetrieveSerializerTest(ApiTestCase):
    serializer_class = serializers.UserRetrieveSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user(full_name=self.TEST_FULL_NAME, phone=self.TEST_PHONE)

    def test_serializer_returns_expected_data_without_address(self):
        expected_data = dict(
            email=self.user.email,
            full_name=self.user.full_name,
            phone=self.user.phone,
            address={},
        )

        serializer = self.serializer_class(instance=self.user)

        self.assertEqual(serializer.data, expected_data)

    def test_serializer_returns_expected_data_with_address(self):
        address = self.create_test_address(self.user)
        self.user.refresh_from_db()

        expected_data = dict(
            email=self.user.email,
            full_name=self.user.full_name,
            phone=self.user.phone,
            address=dict(
                city=address.city,
                street=address.street,
                number=address.number,
            ),
        )

        serializer = self.serializer_class(instance=self.user)

        self.assertEqual(serializer.data, expected_data)


class UserSetPasswordSerializerTest(ApiTestCase):
    serializer_class = serializers.UserSetPasswordSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(
            password=self.TEST_PASSWORD,
            new_password='new_password123!@#',
        )

    def test_expected_field_are_required(self):
        self.assert_required_serializer_fields(self.serializer_class, self.data, ['password', 'new_password'])

    def test_serializer_updates_user_password(self):
        self.assertFalse(self.user.check_password(self.data['new_password']))

        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password(self.data['new_password']))

    def test_serializer_doesnt_update_user_password_with_not_user_password(self):
        self.data['password'] = 'invalid_password'

        serializer = self.serializer_class(self.user, self.data)
        with self.assertRaisesRegex(ValidationError, r'password.+invalid_password.'):
            serializer.is_valid(raise_exception=True)

    def test_serializer_doesnt_update_user_password_with_invalid_new_password(self):
        self.data['new_password'] = '123'

        serializer = self.serializer_class(self.user, self.data)
        with self.assertRaisesRegex(ValidationError, r'password_too_short.+password_entirely_numeric'):
            serializer.is_valid(raise_exception=True)


class UserRegisterSerializerTest(ApiTestCase):
    serializer_class = serializers.UserRegisterSerializer
    model = User

    def setUp(self) -> None:
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            full_name=self.TEST_FULL_NAME,
            phone=self.TEST_PHONE,
        )

    def test_serializer_inherits_expected_mixins(self):
        expected_mixins = [mixins.PasswordValidationMixin, mixins.PhoneNumberValidationMixin]
        for mixin in expected_mixins:
            self.assert_is_subclass(self.serializer_class, mixin)

    def test_serializer_creates_user(self):
        self.assertEqual(self.model.objects.count(), 0)

        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(self.model.objects.count(), 1)

        user = self.model.objects.first()

        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertEqual(user.full_name, self.data['full_name'])
        self.assertEqual(user.phone, self.data['phone'])

    def test_expected_fields_are_write_only(self):
        self.assert_write_only_serializer_fields(self.serializer_class, self.data, ['password'])

    def test_expected_fields_are_required(self):
        self.assert_required_serializer_fields(
            self.serializer_class, self.data, ['email', 'password', 'full_name', 'phone']
        )


class UserUpdateSerializerTest(ApiTestCase):
    serializer_class = serializers.UserUpdateSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.update_data = dict(
            email='new.email@test.com',
        )

        self.expected_data = dict(
            **self.update_data,
            full_name=self.user.full_name,
            phone=self.user.phone,
            address={},
        )

    def test_serializer_inherits_expected_mixins(self):
        expected_mixins = (mixins.PhoneNumberValidationMixin, AddressCreateUpdateMixin)
        self.assert_is_subclass(self.serializer_class, expected_mixins)

    def test_serializer_returns_expected_data_without_address(self):
        serializer = self.serializer_class(self.user, self.update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(serializer.data, self.expected_data)

    def test_serializer_returns_expected_data_with_address(self):
        address = self.create_test_address(self.user)
        self.user.refresh_from_db()
        self.expected_data['address'] = dict(
            city=address.city,
            street=address.street,
            number=address.number,
        )

        serializer = self.serializer_class(self.user, self.update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(serializer.data, self.expected_data)


class UserDisableSerializerTest(ApiTestCase):
    serializer_class = UserDisableSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(
            password=self.TEST_PASSWORD,
        )

    # TODO password must be required
    # def test_expected_fields_are_required(self):
    #     self.assert_required_serializer_fields(self.serializer_class, self.data, ['password'])

    def serializer_doesnt_disable_user_by_not_user_password(self):
        self.data['password'] = 'other_password'
        serializer = self.serializer_class(self.user, self.data)
        with self.assertRaisesRegex(ValidationError, r'invalid_password'):
            serializer.is_valid(raise_exception=True)

    def serializer_doesnt_disable_superuser(self):
        self.user.is_superuser = True
        self.user.save()

        serializer = self.serializer_class(self.user, self.data)

        with self.assertRaisesRegex(ValidationError, r'disable_staff'):
            serializer.is_valid(raise_exception=True)

    def serializer_doesnt_disable_staff_user(self):
        self.user.is_staff = True
        self.user.save()

        serializer = self.serializer_class(self.user, self.data)

        with self.assertRaisesRegex(ValidationError, r'disable_staff'):
            serializer.is_valid(raise_exception=True)

    def test_serializer_replaces_user_data(self):
        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        self.user.refresh_from_db()

        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.email, f'user.{self.user.pk}@disabled.com')
        self.assertEqual(self.user.full_name, f'disabled user {self.user.pk}')
        self.assertEqual(self.user.phone, '+38 (012) 345 6789')
        self.assertEqual(self.user.password, '-')

    def test_serializer_replaces_user_address_data(self):
        address = self.create_test_address(self.user)
        self.user.refresh_from_db()

        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        address.refresh_from_db()

        self.assertEqual(address.number, '-')

    def test_serializer_blacklists_refresh_tokens_that_are_associated_with_user(self):
        tokens: list[RefreshToken] = [self.user.refresh_token, self.user.refresh_token, self.user.refresh_token]

        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        for token in tokens:
            self.assertRaises(TokenError, token.check_blacklist)

    def test_serializer_doesnt_raise_error_for_blacklisted_refresh_token(self):
        blacklisted_token = self.user.refresh_token
        blacklisted_token.blacklist()

        self.assertRaises(TokenError, blacklisted_token.check_blacklist)

        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))  # not raise
