from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from accounts import serializers, services

User = get_user_model()


class UserRegisterSerializerTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.UserRegisterSerializer
        self.data = {
            'email': 'test@test.com',
            'password': 'qwe123!@#',
            'phone': '+380123456789',
        }

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

    def test_password_field_is_write_only(self):
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('password', serializer.data)

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
        normalized_phone = services.normalize_phone_to_ukrainian_format(self.data['phone'])
        serializer = self.serializer_class(data=self.data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['phone'], normalized_phone)
