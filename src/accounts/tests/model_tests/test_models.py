from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import Token

from accounts import models
from accounts.models.managers import UserManager
from utils.tests.cases import BaseTestCase


class UserModelTest(BaseTestCase):
    model = models.User

    def setUp(self) -> None:
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
        )

    def test_model_inherits_classes(self):
        self.assert_is_subclass(self.model, (PermissionsMixin, AbstractBaseUser))

    def test_email_field_is_username_field(self):
        self.assertEqual(self.model.USERNAME_FIELD, 'email')

    def test_full_name_field_has_2_min_length(self):
        with self.assertRaisesRegex(ValidationError, r'Ensure this value has at least 2 characters'):
            user = self.model(**self.data, full_name='a')
            user.full_clean()

    def test_phone_field_must_be_at_correct_format(self):
        # Check valid phones
        user = self.model(**self.data, phone='+38 (012) 345 6789')
        user.full_clean()  # not raise

        # Check invalid phones
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
        for phone in invalid_phones:
            user = self.model(**self.data, phone=phone)
            with self.assertRaisesRegex(
                ValidationError, r'The phone number must be in the following format: \+38 \(012\) 345 6789.'
            ):
                user.full_clean()

    def test_updated_at_field_is_set_auto_after_every_save(self):
        field = self.model.updated_at.field
        self.assertTrue(field.auto_now)

    def test_joined_at_field_is_set_auto_only_at_first_save(self):
        field = self.model.joined_at.field
        self.assertTrue(field.auto_now_add)

    def test_access_token_property_returns_access_token(self):
        user = self.model.objects.create(**self.data)
        self.assertIsInstance(user.access_token, Token)

    def test_refresh_token_returns_refresh_token(self):
        user = self.model.objects.create(**self.data)
        self.assertIsInstance(user.refresh_token, Token)

    def test_refresh_token_and_access_token_dont_match(self):
        user = self.model.objects.create(**self.data)
        self.assertNotEqual(user.access_token, user.refresh_token)

    def test_user_is_specified_in_the_auth_user_model_setting(self):
        self.assertIs(self.model, get_user_model())

    def test_model_has_expected_manager(self):
        self.assertIsInstance(self.model.objects, UserManager)
