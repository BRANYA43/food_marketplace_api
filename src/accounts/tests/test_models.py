from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from rest_framework_simplejwt.tokens import Token

from accounts import models
from accounts.managers import UserManager
from utils.tests import ApiTestCase


class UserModelTest(ApiTestCase):
    model = models.User

    def setUp(self) -> None:
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
        )

    def test_model_inherits_permissions_mixin(self):
        self.assert_is_subclass(self.model, PermissionsMixin)

    def test_model_inherits_abstract_base_user(self):
        self.assert_is_subclass(self.model, AbstractBaseUser)

    def test_email_field_is_required(self):
        self.assert_required_model_field(self.model, 'email', self.data, 'email.+This field cannot be blank')

    def test_password_field_is_required(self):
        self.assert_required_model_field(self.model, 'password', self.data, 'password.+This field cannot be blank')

    def test_email_field_is_username_field(self):
        self.assertEqual(self.model.USERNAME_FIELD, 'email')

    def test_full_name_field_is_optional(self):
        self.assert_optional_model_field(self.model, 'full_name', self.data)

    def test_full_name_field_has_2_min_length(self):
        self.data['full_name'] = 'a'
        self.assert_validation_model_field(self.model, self.data, 'Ensure this value has at least 2 characters')

    def test_phone_field_is_optional(self):
        self.assert_optional_model_field(self.model, 'phone', self.data)

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
            self.data['phone'] = phone
            self.assert_validation_model_field(
                self.model,
                self.data,
                r'The phone number must be in the following format: \+38 \(012\) 345 6789',
            )

    def test_is_staff_field_is_false_by_default(self):
        self.assert_model_field_default_value(self.model, 'is_staff', self.data, False)

    # TODO Must be False by default. Only after confirmation of email it is True
    def test_is_active_field_is_true_by_default(self):
        self.assert_model_field_default_value(self.model, 'is_active', self.data, True)

    def test_updated_at_field_is_set_auto_after_every_save(self):
        user = self.model.objects.create(**self.data)
        self.assertAlmostEqual(user.updated_at.timestamp(), datetime.now().timestamp(), delta=1)

        old_update_at = user.updated_at
        user.full_name = 'Rick Sanchez'
        user.save()
        self.assertNotEqual(user.updated_at, old_update_at)

    def test_joined_at_field_is_set_auto_only_at_first_save(self):
        user = self.model.objects.create(**self.data)
        self.assertAlmostEqual(user.joined_at.timestamp(), datetime.now().timestamp(), delta=1)

        old_joined_at = user.joined_at
        user.full_name = 'Rick Sanchez'
        user.save()
        self.assertEqual(user.joined_at, old_joined_at)

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
