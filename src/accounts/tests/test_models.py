from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import Token

from accounts import models, managers
from utils.models import Address
from utils.tests import APITestCase


class UserAddressTest(APITestCase):
    def setUp(self) -> None:
        self.model_class = models.UserAddress
        self.user = self.create_test_user()
        self.data = dict(
            user=self.user,
            region='region',
            city='city',
            street='street',
            number='0',
        )

    def test_model_inherits_address_model(self):
        self.assertTrue(issubclass(self.model_class, Address))

    def test_user_field_is_required(self):
        del self.data['user']
        with self.assertRaisesRegex(IntegrityError, r'NOT NULL'):
            self.model_class.objects.create(**self.data)

    def test_string_representation_returns_user(self):
        address = self.model_class.objects.create(**self.data)
        self.assertEqual(str(address), str(self.user))


class UserModelTest(APITestCase):
    def setUp(self) -> None:
        self.model_class = models.User
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
        )

    def test_model_inherits_permissions_mixin(self):
        self.assertTrue(issubclass(self.model_class, PermissionsMixin))

    def test_model_inherits_abstract_base_user(self):
        self.assertTrue(issubclass(self.model_class, AbstractBaseUser))

    def test_email_field_is_required(self):
        del self.data['email']
        with self.assertRaisesRegex(ValidationError, r'This field cannot be blank\.'):
            user = self.model_class(**self.data)
            user.full_clean()

    def test_email_field_is_username_field(self):
        self.assertEqual(self.model_class.USERNAME_FIELD, 'email')

    def test_full_name_field_is_optional(self):
        user = self.model_class(**self.data, full_name=None)
        user.full_clean()  # not raise

    def test_full_name_field_has_2_min_length(self):
        user = self.model_class(**self.data, full_name='l')
        with self.assertRaisesRegex(ValidationError, 'Ensure this value has at least 2 characters'):
            user.full_clean()

    def test_phone_field_is_optional(self):
        user = self.model_class(**self.data, phone=None)
        user.full_clean()

    def test_phone_field_must_be_at_correct_format(self):
        valid_phones = [
            '+38 (050) 000 0000',
        ]
        invalid_phones = [
            '+380500000000',
            '+38 050 000 00 00',
            '+38 050 00 00 000',
            '0500000000',
            '050 000 00 00',
            '050 00 00 000',
            '+1 (050) 000 00-00',
            '380500000000',
            '050-000-0000',
            '+38 050-00-00-00',
            '050 00 00 00',
            '+38 05000000 000',
        ]

        # Check valid phones
        for phone in valid_phones:
            user = self.model_class(**self.data, phone=phone)
            user.full_clean()  # not raise

        # Check invalid phones
        for phone in invalid_phones:
            with self.assertRaisesRegex(ValidationError, r'User phone must be at one of format: \+38 \(050\) 000 0000'):
                user = self.model_class(**self.data, phone=phone)
                user.full_clean()

    def test_is_staff_field_is_false_by_default(self):
        user = self.model_class(**self.data)
        self.assertFalse(user.is_staff)

    def test_is_active_field_is_true_by_default(self):
        user = self.model_class(**self.data)
        self.assertTrue(user.is_active)  # TODO Must be False by default. Only after confirmation of email it is True

    def test_updated_at_field_is_set_auto_after_every_save(self):
        user = self.model_class.objects.create(**self.data)
        self.assertAlmostEqual(user.updated_at.timestamp(), datetime.now().timestamp(), delta=1)

        old_update_at = user.updated_at
        user.full_name = 'Rick Sanchez'
        user.save()
        self.assertNotEqual(user.updated_at, old_update_at)

    def test_joined_at_field_is_set_auto_only_at_first_save(self):
        user = self.model_class.objects.create(**self.data)
        self.assertAlmostEqual(user.joined_at.timestamp(), datetime.now().timestamp(), delta=1)

        old_joined_at = user.joined_at
        user.full_name = 'Rick Sanchez'
        user.save()
        self.assertEqual(user.joined_at, old_joined_at)

    def test_model_representation_returns_user_email(self):
        user = self.model_class(**self.data)

        self.assertEqual(str(user), user.email)

    def test_model_is_auth_user_model(self):
        self.assertIs(self.model_class, get_user_model())

    def test_access_token_property_returns_access_token(self):
        user = self.model_class.objects.create_user(**self.data)
        self.assertIsInstance(user.access_token, Token)

    def test_refresh_token_returns_refresh_token(self):
        user = self.model_class.objects.create_user(**self.data)
        self.assertIsInstance(user.refresh_token, Token)

    def test_refresh_token_and_access_token_dont_match(self):
        user = self.model_class.objects.create_user(**self.data)
        self.assertNotEqual(user.access_token, user.refresh_token)

    def test_model_uses_expected_object_manager(self):
        self.assertIsInstance(self.model_class.objects, managers.UserManager)
