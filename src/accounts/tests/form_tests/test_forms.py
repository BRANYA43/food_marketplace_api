from django.contrib.auth import get_user_model

from accounts.forms import BaseUserCreationForm, StaffCreationForm, CustomerCreationForm
from utils.tests.cases import BaseTestCase

User = get_user_model()


class CustomerCreationFormTest(BaseTestCase):
    form_class = CustomerCreationForm
    model = User

    def setUp(self) -> None:
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            confirming_password=self.TEST_PASSWORD,
            full_name=self.TEST_FULL_NAME,
            phone=self.TEST_PHONE,
        )

    def test_form_inherits_base_user_creation_form(self):
        self.assert_is_subclass(self.form_class, BaseUserCreationForm)

    def test_form_creates_user(self):
        self.assertEqual(self.model.objects.count(), 0)

        form = self.form_class(data=self.data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(self.model.objects.count(), 1)

        user = self.model.objects.first()

        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertEqual(user.full_name, self.data['full_name'])
        self.assertEqual(user.phone, self.data['phone'])


class StaffCreationFormTest(BaseTestCase):
    form_class = StaffCreationForm
    model = User

    def setUp(self) -> None:
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            confirming_password=self.TEST_PASSWORD,
        )

    def test_form_inherits_base_user_creation_form(self):
        self.assert_is_subclass(self.form_class, BaseUserCreationForm)

    def test_form_creates_user(self):
        self.assertEqual(self.model.objects.count(), 0)

        form = self.form_class(data=self.data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(self.model.objects.count(), 1)

        user = self.model.objects.first()

        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)


class BaseUserCreationFormTest(BaseTestCase):
    form_class = BaseUserCreationForm
    model = User

    def setUp(self) -> None:
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            confirming_password=self.TEST_PASSWORD,
        )

    def test_form_validates_password_mismatch(self):
        self.data['confirming_password'] = 'mismatched_password'

        form = self.form_class(data=self.data)
        self.assertFalse(form.is_valid())

        self.assertFormError(form, 'confirming_password', ["The two password fields didn't match."])

    def test_form_validates_invalid_password(self):
        self.data['password'] = '1'

        form = self.form_class(data=self.data)
        self.assertFalse(form.is_valid())

        self.assertRegex(
            str(form.errors),
            'This password is too short. It must contain at least 8 characters.+This password is entirely numeric',
        )

    def test_form_creates_user(self):
        self.assertEqual(self.model.objects.count(), 0)

        form = self.form_class(data=self.data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(self.model.objects.count(), 1)

        user = self.model.objects.first()

        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
