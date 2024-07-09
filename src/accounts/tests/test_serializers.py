from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from utils.tests import APITestCase

from accounts import serializers, services, models

User = get_user_model()


class UserAddressSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.UserAddressSerializer
        self.address_model_class = models.UserAddress
        self.data = dict(
            region='region',
            city='city',
            street='street',
            number='0',
        )

    def test_serializer_inherit_model_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, ModelSerializer))

    def test_user_field_is_optional(self):
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_user_field_is_write_only(self):
        self.data['user'] = self.create_test_user().pk
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid())

        self.assertIsNone(serializer.data.get('user'))

    def test_region_field_is_required(self):
        del self.data['region']
        serializer = self.serializer_class(data=self.data)
        with self.assertRaisesRegex(ValidationError, r"code='required'"):
            serializer.is_valid(raise_exception=True)

    def test_city_field_is_required(self):
        del self.data['city']
        serializer = self.serializer_class(data=self.data)
        with self.assertRaisesRegex(ValidationError, r"code='required'"):
            serializer.is_valid(raise_exception=True)

    def test_street_field_is_required(self):
        del self.data['street']
        serializer = self.serializer_class(data=self.data)
        with self.assertRaisesRegex(ValidationError, r"code='required'"):
            serializer.is_valid(raise_exception=True)

    def test_number_field_is_required(self):
        del self.data['number']
        serializer = self.serializer_class(data=self.data)
        with self.assertRaisesRegex(ValidationError, r"code='required'"):
            serializer.is_valid(raise_exception=True)

    def test_village_field_is_optional(self):
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_creates_address(self):
        self.assertEqual(self.address_model_class.objects.count(), 0)

        user = self.create_test_user()
        self.data['user'] = user.pk
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        address = self.address_model_class.objects.get(user=user)
        del self.data['user']
        for field, value in self.data.items():
            self.assertEqual(getattr(address, field, value), self.data[field])

    def test_serializer_updates_address(self):
        user = self.create_test_user()
        self.data['user'] = user
        address = self.address_model_class.objects.create(**self.data)

        update_data = dict(region='new region')
        serializer = self.serializer_class(address, update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        db_address = self.address_model_class.objects.get(user=user)

        self.assertEqual(db_address.region, update_data['region'])

    def test_serializer_returns_expected_data(self):
        user = self.create_test_user()
        self.data['user'] = user.pk

        expected_data = dict(
            region=self.data['region'],
            city=self.data['city'],
            village=None,
            street=self.data['street'],
            number=self.data['number'],
        )

        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertDictEqual(serializer.data, expected_data)


class UserPasswordSetSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.UserPasswordSetSerializer
        self.user = self.create_test_user()
        self.request = self.request_factory.get('/')
        self.request.user = self.user
        self.data = dict(
            password=self.TEST_PASSWORD,
            new_password='new_password123!@#',
        )

    def test_serializer_inherits_model_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, ModelSerializer))

    def test_serializer_updates_user_password_correctly(self):
        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertTrue(self.user.check_password(self.data['new_password']))

    def test_serializer_doesnt_update_user_for_invalid_password(self):
        self.data['password'] = 'invalid_password'
        serializer = self.serializer_class(self.user, self.data)
        with self.assertRaisesRegex(ValidationError, r"Entered password isn't user password."):
            serializer.is_valid(raise_exception=True)

    def test_serializer_doesnt_update_user_for_invalid_new_password(self):
        self.data['new_password'] = '1'
        serializer = self.serializer_class(self.user, self.data)
        with self.assertRaisesRegex(
            ValidationError, r'.+password_too_short.+password_too_common.+password_entirely_numeric'
        ):
            serializer.is_valid(raise_exception=True)

    def test_serializer_returns_empty_data(self):
        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(serializer.data, {})


class UserProfileSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.UserProfileSerializer
        self.address_model_class = models.UserAddress
        self.user = self.create_test_user(**self.rick_data)
        self.data = self.morty_data
        del self.data['password']

    def test_serializer_inherits_base_user_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, serializers.BaseUserSerializer))

    def test_address_field_is_optional(self):
        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertIsNone(serializer.data.get('address'))

    def test_serializer_updates_user(self):
        for field, value in self.data.items():
            self.assertNotEqual(getattr(self.user, field), value)

        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        for field, value in self.data.items():
            self.assertEqual(getattr(self.user, field), value)

    def test_serializer_updates_user_and_create_address(self):
        # assert user
        for field, value in self.data.items():
            self.assertNotEqual(getattr(self.user, field), value)
        self.assertIsNone(getattr(self.user, 'address', None))

        self.data['address'] = dict(
            region='region',
            city='city',
            street='street',
            number='0',
        )

        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        # assert address
        address_data = self.data.pop('address')
        address = self.user.address
        for field, value in address_data.items():
            self.assertEqual(getattr(address, field), value)
        self.assertIsNone(address.village)

        # assert user
        for field, value in self.data.items():
            self.assertEqual(getattr(self.user, field), value)

    def test_serializer_updates_user_and_address(self):
        address = self.address_model_class.objects.create(
            user=self.user,
            region='region',
            city='city',
            street='street',
            number='0',
        )

        self.data['address'] = dict(
            region='new region',
            city='new city',
            street='new street',
            number='1',
        )

        # assert user
        for field, value in self.data.items():
            self.assertNotEqual(getattr(self.user, field), value)

        # assert address
        for field, value in self.data['address'].items():
            self.assertNotEqual(getattr(address, field), value)

        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        # assert address
        address_data = self.data.pop('address')
        address.refresh_from_db()
        for field, value in address_data.items():
            self.assertEqual(getattr(address, field), value)
        self.assertIsNone(address.village)

        # assert user
        for field, value in self.data.items():
            self.assertEqual(getattr(self.user, field), value)

    def test_serializer_return_expected_data_without_address(self):
        expected_data = dict(
            **self.data,
            address=None,
        )

        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(serializer.data, expected_data)

    def test_serializer_return_expected_data_with_address(self):
        self.data['address'] = dict(
            region='region',
            city='city',
            village=None,
            street='street',
            number='0',
        )
        expected_data = dict(
            **self.data,
        )

        serializer = self.serializer_class(self.user, self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(serializer.data, expected_data)


class UserRegisterSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.UserRegisterSerializer
        self.data = self.rick_data

    def test_serializer_inherits_base_user_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, serializers.BaseUserSerializer))

    def test_serializer_creates_user_correctly(self):
        self.assertEqual(User.objects.count(), 0)

        serializer = self.serializer_class(data=self.data)

        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.id, User.objects.first().id)
        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertIsNotNone(user.phone)

    def test_serializer_is_invalid_with_invalid_credentials(self):
        invalid_data = dict(
            email='invalid.email.com',
            password='qwe',
            full_name='qw',
            phone='123',
        )
        serializer = self.serializer_class(data=invalid_data)

        self.assertFalse(serializer.is_valid())

    def test_serializer_is_invalid_with_empty_credentials(self):
        serializer = self.serializer_class(data={})

        self.assertFalse(serializer.is_valid())

    def test_phone_is_required_field(self):
        del self.data['phone']
        serializer = self.serializer_class(data=self.data)
        self.assertRaisesRegex(
            ValidationError,
            r'This field is required',
            serializer.is_valid,
            raise_exception=True,
        )

    def test_full_name_is_required_field(self):
        del self.data['full_name']
        serializer = self.serializer_class(data=self.data)
        self.assertRaisesRegex(
            ValidationError,
            r'This field is required',
            serializer.is_valid,
            raise_exception=True,
        )

    def test_serializer_doesnt_register_user_for_invalid_password(self):
        self.data['password'] = '123'
        serializer = self.serializer_class(data=self.data)
        with self.assertRaisesRegex(
            ValidationError, r'.+password_too_short.+password_too_common.+password_entirely_numeric'
        ):
            serializer.is_valid(raise_exception=True)


class BaseUserSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.BaseUserSerializer
        self.data = {
            'email': self.TEST_EMAIL,
            'password': self.TEST_PASSWORD,
        }

    def test_password_field_is_write_only(self):
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('password', serializer.data)

    def test_password_field_has_min_length_8(self):
        self.data['password'] = 'qwe'
        serializer = self.serializer_class(data=self.data)
        self.assertRaisesRegex(
            ValidationError,
            r'Ensure this field has at least 8 characters\.',
            serializer.is_valid,
            raise_exception=True,
        )

    def test_full_name_field_has_min_length_3(self):
        self.data['full_name'] = 'qw'
        serializer = self.serializer_class(data=self.data)
        self.assertRaisesRegex(
            ValidationError,
            r'Ensure this field has at least 3 characters\.',
            serializer.is_valid,
            raise_exception=True,
        )

    def test_serializer_validates_phone(self):
        invalid_phone = '+38 1234 56 7890'
        self.data['phone'] = invalid_phone
        serializer = self.serializer_class(data=self.data)

        self.assertFalse(serializer.is_valid())
        self.assertRaisesRegex(
            ValidationError,
            r'Phone must be at ukrainian format\. Example \+38 XXX XXX XXXX\.',
            serializer.is_valid,
            raise_exception=True,
        )

    def test_serializer_normalize_phone(self):
        self.data['phone'] = '+380123456789'
        normalized_phone = services.normalize_phone_to_ukrainian_format(self.data['phone'])
        serializer = self.serializer_class(data=self.data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['phone'], normalized_phone)
