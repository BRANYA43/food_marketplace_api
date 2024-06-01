from accounts import managers
from accounts import models
from django.test import TestCase


class UserManagerTest(TestCase):
    def setUp(self) -> None:
        self.manager = managers.UserManager()
        self.manager.model = models.User

        self.data = {
            'email': 'test@test.com',
            'password': 'qwe123!@#',
        }

    def test_manager_doesnt_create_user_or_superuser_if_email_is_none(self):
        self.data['email'] = None

        with self.assertRaisesRegex(ValueError, r'Email cannot be empty.'):
            self.manager.create_user(**self.data)

        with self.assertRaisesRegex(ValueError, r'Email cannot be empty.'):
            self.manager.create_superuser(**self.data)

    def test_manager_doesnt_create_user_or_superuser_if_password_is_none(self):
        self.data['password'] = None

        with self.assertRaisesRegex(ValueError, r'Password cannot be empty.'):
            self.manager.create_user(**self.data)

        with self.assertRaisesRegex(ValueError, r'Password cannot be empty.'):
            self.manager.create_superuser(**self.data)

    def test_manager_creates_user_correct(self):
        user = self.manager.create_user(**self.data)
        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertEqual(
            user.is_active, True
        )  # TODO it can be false by default.Only after confirmation of email it is True
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    def test_manager_create_superuser_correct(self):
        superuser = self.manager.create_superuser(**self.data)
        self.assertEqual(superuser.email, self.data['email'])
        self.assertTrue(superuser.check_password(self.data['password']))
        self.assertEqual(superuser.is_active, True)
        self.assertEqual(superuser.is_staff, True)
        self.assertEqual(superuser.is_superuser, True)
