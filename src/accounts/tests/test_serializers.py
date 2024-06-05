from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from utils.tests import APITestCase

from accounts import serializers, services

User = get_user_model()


class UserProfileSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.UserProfileSerializer
        self.data = {
            'email': 'another.email@test.com',
            'phone': '+38 (98) 765 4321',
            'full_name': 'Morty',
        }
        self.user = self.create_test_user(phone='+38 (012) 345 6789', full_name='Rick Sanchez')

    def test_serializer_gets_expected_data(self):
        serializer = self.serializer_class(instance=self.user)
        for field in self.data.keys():
            self.assertEqual(serializer.data[field], getattr(self.user, field))

    def test_all_fields_is_read_only_fields(self):
        serializer = self.serializer_class(instance=self.user, data=self.data)
        serializer.is_valid()
        serializer.save()

        for field in self.data.keys():
            self.assertEqual(serializer.data[field], getattr(self.user, field))


class UserRegisterSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.UserRegisterSerializer
        self.data = {
            'email': self.TEST_EMAIL,
            'password': self.TEST_PASSWORD,
            'phone': '+380123456789',
            'full_name': 'Rick Sanchez',
        }

    def test_serializer_inherits_base_user_serializer(self):
        self.assertTrue(issubclass(self.serializer_class, serializers.BaseUserSerializer))

    def test_serializer_creates_user_correctly(self):
        serializer = self.serializer_class(data=self.data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(User.objects.count(), 0)

        user = serializer.save()

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.id, User.objects.first().id)
        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertIsNotNone(user.phone)

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
