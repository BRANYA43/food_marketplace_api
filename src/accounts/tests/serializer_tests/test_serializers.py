from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    UserSetPasswordSerializer,
    UserRegisterSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
    UserDisableSerializer,
)
from accounts.serializers.mixins import PasswordValidationMixin, PhoneNumberValidationMixin
from utils.serializers.mixins import AddressCreateUpdateMixin
from utils.tests.cases import SerializerTestCase

User = get_user_model()


class UserSetPasswordSerializerTest(SerializerTestCase):
    serializer_class = UserSetPasswordSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(
            password=self.TEST_PASSWORD,
            new_password='new_password123!@#',
        )

    def test_expected_field_are_required(self):
        self.assert_required_fields(self.serializer_class, ['password', 'new_password'])

    def test_expected_fields_are_write_only(self):
        self.assert_fields_are_write_only(self.serializer_class, ['password', 'new_password'])

    def test_serializer_updates_user_password(self):
        self.assertFalse(self.user.check_password(self.data['new_password']))

        self.create_serializer_deprecated(self.serializer_class, input_data=self.data, instance=self.user, save=True)

        self.assertTrue(self.user.check_password(self.data['new_password']))

    def test_serializer_doesnt_update_user_password_with_not_user_password(self):
        self.data['password'] = 'invalid_password'

        with self.assertRaisesRegex(ValidationError, r'password.+invalid_password.'):
            self.create_serializer_deprecated(
                self.serializer_class,
                input_data=self.data,
                instance=self.user,
            )

    def test_serializer_doesnt_update_user_password_with_invalid_new_password(self):
        self.data['new_password'] = '123'

        with self.assertRaisesRegex(ValidationError, r'password_too_short.+password_entirely_numeric'):
            self.create_serializer_deprecated(
                self.serializer_class,
                input_data=self.data,
                instance=self.user,
            )


class UserRegisterSerializerTest(SerializerTestCase):
    serializer_class = UserRegisterSerializer
    user_model = User

    def setUp(self) -> None:
        self.input_data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            full_name=self.TEST_FULL_NAME,
            phone=self.TEST_PHONE,
        )

    def test_serializer_inherits_expected_mixins(self):
        self.assert_is_subclass(self.serializer_class, (PasswordValidationMixin, PhoneNumberValidationMixin))

    def test_expected_fields_are_required(self):
        self.assert_required_fields(self.serializer_class, ['email', 'password', 'full_name', 'phone'])

    def test_expected_fields_are_write_only(self):
        self.assert_fields_are_write_only(self.serializer_class, ['password'])

    def test_serializer_creates_user(self):
        self.assertEqual(self.user_model.objects.count(), 0)

        self.create_serializer_deprecated(
            self.serializer_class,
            input_data=self.input_data,
            save=True,
        )

        self.assertEqual(self.user_model.objects.count(), 1)

        user = self.user_model.objects.first()

        self.assertTrue(user.check_password(self.input_data.pop('password')))
        self.assert_model_instance(user, self.input_data)


class UserRetrieveSerializerTest(SerializerTestCase):
    serializer_class = UserRetrieveSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user(full_name=self.TEST_FULL_NAME, phone=self.TEST_PHONE)

    def test_expected_fields_are_read_only(self):
        self.assert_fields_are_read_only(self.serializer_class, ['email', 'full_name', 'phone', 'address'])

    def test_serializer_returns_expected_data_without_address(self):
        self.assert_output_serializer_data(
            self.serializer_class,
            instance=self.user,
            output_data=dict(
                email=self.user.email,
                full_name=self.user.full_name,
                phone=self.user.phone,
                address={},
            ),
        )

    def test_serializer_returns_expected_data_with_address(self):
        address = self.create_test_address(self.user)
        self.user.refresh_from_db()

        self.assert_output_serializer_data(
            self.serializer_class,
            instance=self.user,
            output_data=dict(
                email=self.user.email,
                full_name=self.user.full_name,
                phone=self.user.phone,
                address=dict(
                    city=address.city,
                    street=address.street,
                    number=address.number,
                ),
            ),
        )


class UserUpdateSerializerTest(SerializerTestCase):
    serializer_class = UserUpdateSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.input_data = dict(
            email='new.email@test.com',
        )

        self.output_data = dict(
            **self.input_data,
            full_name=self.user.full_name,
            phone=self.user.phone,
            address={},
        )

    def test_serializer_inherits_mixins(self):
        self.assert_is_subclass(self.serializer_class, (PhoneNumberValidationMixin, AddressCreateUpdateMixin))

    def test_expected_fields_are_required(self):
        self.assert_required_fields(self.serializer_class, ['email', 'full_name', 'phone'])

    def test_expected_fields_are_optional(self):
        self.assert_optional_fields(self.serializer_class, ['address'])

    def test_serializer_returns_data_without_address(self):
        self.assert_output_serializer_data(
            self.serializer_class,
            instance=self.user,
            input_data=self.input_data,
            output_data=self.output_data,
            partial=True,
            save=True,
        )


class UserDisableSerializerTest(SerializerTestCase):
    serializer_class = UserDisableSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.data = dict(
            password=self.TEST_PASSWORD,
        )

    def test_expected_fields_are_required(self):
        self.assert_required_fields(self.serializer_class, ['password'])

    def serializer_doesnt_disable_user_by_not_user_password(self):
        self.data['password'] = 'other_password'
        with self.assertRaisesRegex(ValidationError, r'invalid_password'):
            self.create_serializer_deprecated(
                self.serializer_class,
                instance=self.user,
                input_data=self.data,
            )

    def serializer_doesnt_disable_superuser(self):
        self.user.is_superuser = True
        self.user.save()

        with self.assertRaisesRegex(ValidationError, r'disable_staff'):
            self.create_serializer_deprecated(
                self.serializer_class,
                instance=self.user,
                input_data=self.data,
            )

    def serializer_doesnt_disable_staff_user(self):
        self.user.is_staff = True
        self.user.save()

        with self.assertRaisesRegex(ValidationError, r'disable_staff'):
            self.create_serializer_deprecated(
                self.serializer_class,
                instance=self.user,
                input_data=self.data,
            )

    def test_serializer_replaces_user_data(self):
        self.create_serializer_deprecated(
            self.serializer_class,
            instance=self.user,
            input_data=self.data,
        )

        self.user.refresh_from_db()

        self.assert_model_instance(
            self.user,
            dict(
                is_active=False,
                email=f'user.{self.user.pk}@disabled.com',
                password='-',
                full_name=f'disabled user {self.user.pk}',
                phone='+38 (012) 345 6789',
            ),
        )

    def test_serializer_replaces_user_address_data(self):
        address = self.create_test_address(self.user)
        self.user.refresh_from_db()

        self.create_serializer_deprecated(
            self.serializer_class,
            instance=self.user,
            input_data=self.data,
        )

        address.refresh_from_db()

        self.assert_model_instance(address, dict(number='-'))

    def test_serializer_blacklists_refresh_tokens_that_are_associated_with_user(self):
        tokens: list[RefreshToken] = [self.user.refresh_token, self.user.refresh_token, self.user.refresh_token]

        self.create_serializer_deprecated(
            self.serializer_class,
            instance=self.user,
            input_data=self.data,
        )

        for token in tokens:
            self.assertRaises(TokenError, token.check_blacklist)

    def test_serializer_doesnt_raise_error_for_blacklisted_refresh_token(self):
        blacklisted_token = self.user.refresh_token
        blacklisted_token.blacklist()

        self.assertRaises(TokenError, blacklisted_token.check_blacklist)

        self.create_serializer_deprecated(
            self.serializer_class,
            instance=self.user,
            input_data=self.data,
        )  # not raise error
