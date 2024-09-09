from accounts.models.managers import UserManager
from accounts import models
from utils.tests.cases import BaseTestCase


class UserManagerTest(BaseTestCase):
    def setUp(self) -> None:
        self.manager = UserManager()
        self.manager.model = models.User

        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
        )

        self.data_with_extras = dict(
            **self.data,
            full_name=self.TEST_FULL_NAME,
            phone=self.TEST_PHONE,
        )

    def test_manager_doesnt_create_user_or_superuser_if_email_is_empty(self):
        self.data['email'] = ''

        with self.assertRaisesRegex(ValueError, r'Email cannot be empty.'):
            self.manager.create_user(**self.data)

        with self.assertRaisesRegex(ValueError, r'Email cannot be empty.'):
            self.manager.create_superuser(**self.data)

    def test_manager_doesnt_create_user_or_superuser_if_password_is_empty(self):
        self.data['password'] = ''

        with self.assertRaisesRegex(ValueError, r'Password cannot be empty.'):
            self.manager.create_user(**self.data)

        with self.assertRaisesRegex(ValueError, r'Password cannot be empty.'):
            self.manager.create_superuser(**self.data)

    # TODO is_active must be false by default. Only after confirmation of email it is True
    def test_manager_creates_user(self):
        user = self.manager.create_user(**self.data)
        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    def test_manager_create_superuser(self):
        superuser = self.manager.create_superuser(**self.data)
        self.assertEqual(superuser.email, self.data['email'])
        self.assertTrue(superuser.check_password(self.data['password']))
        self.assertEqual(superuser.is_active, True)
        self.assertEqual(superuser.is_staff, True)
        self.assertEqual(superuser.is_superuser, True)

    # TODO is_active must be false by default. Only after confirmation of email it is True
    def test_manager_create_user_with_extra_fields_correctly(self):
        user = self.manager.create_user(**self.data_with_extras)
        self.assertEqual(user.email, self.data_with_extras['email'])
        self.assertTrue(user.check_password(self.data_with_extras['password']))
        self.assertEqual(user.full_name, self.data_with_extras['full_name'])
        self.assertEqual(user.phone, self.data_with_extras['phone'])
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    def test_manager_create_superuser_with_extra_fields_correctly(self):
        superuser = self.manager.create_superuser(**self.data_with_extras)
        self.assertEqual(superuser.email, self.data_with_extras['email'])
        self.assertTrue(superuser.check_password(self.data_with_extras['password']))
        self.assertEqual(superuser.full_name, self.data_with_extras['full_name'])
        self.assertEqual(superuser.phone, self.data_with_extras['phone'])
        self.assertEqual(superuser.is_active, True)
        self.assertEqual(superuser.is_staff, True)
        self.assertEqual(superuser.is_superuser, True)
