from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from accounts.serializers import serializers, mixins
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
        expected_fields = ['password']
        serializer = self.serializer_class(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        for field in expected_fields:
            self.assertIsNone(serializer.data.get(field))

    def test_expected_field_is_required(self):
        expected_fields = ['email', 'password', 'full_name', 'phone']

        for field in expected_fields:
            data = self.data.copy()
            del data[field]
            serializer = self.serializer_class(data=data)
            with self.assertRaisesRegex(ValidationError, rf'{field}.+required'):
                self.assertTrue(serializer.is_valid(raise_exception=True))
