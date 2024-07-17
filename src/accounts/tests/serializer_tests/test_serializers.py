from django.contrib.auth import get_user_model

from accounts.serializers import serializers, mixins
from utils.serializers.mixins import AddressCreateUpdateMixin
from utils.tests import ApiTestCase

User = get_user_model()


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

    def test_expected_fields_is_write_only(self):
        self.assert_write_only_serializer_fields(self.serializer_class, self.data, ['password'])

    def test_expected_field_is_required(self):
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
