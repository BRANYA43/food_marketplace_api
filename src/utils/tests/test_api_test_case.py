from unittest.mock import MagicMock, patch

from django.core.validators import MinLengthValidator
from django.db import models

from utils.tests import ApiTestCase


class TestModel(models.Model):
    required_field = models.CharField(max_length=10, validators=[MinLengthValidator(2)])
    optional_field = models.CharField(max_length=10, null=True, blank=True)
    default_field = models.CharField(max_length=10, default='1')
    default_true_field = models.BooleanField(default=True)
    default_false_field = models.BooleanField(default=False)

    class Meta:
        managed = False


class ApiTestCaseTest(ApiTestCase):
    def test_assert_is_subclass(self):
        class Parent:
            pass

        class Children(Parent):
            pass

        class Another:
            pass

        self.assert_is_subclass(Children, Parent)  # not raise

        with self.assertRaisesRegex(
            AssertionError,
            rf'{Another} is not subclass of {Parent}.',
        ):
            self.assert_is_subclass(Another, Parent)

    def test_assert_response_status(self):
        mock_response = MagicMock(status_code=200)
        self.assert_response_status(mock_response, 200)  # not raise

        with self.assertRaisesRegex(
            AssertionError, rf'Expected response status code "300", but got "{mock_response.status_code}".'
        ):
            self.assert_response_status(mock_response, 300)

    @patch('rest_framework.test.APIClient.get')
    def test_assert_allowed_method(self, mock_client_get: MagicMock):
        mock_response = MagicMock(status_code=200)
        mock_client_get.return_value = mock_response
        url = '/'

        self.assert_allowed_method(url, 'get', 200)  # not raise

        with self.assertRaisesRegex(
            AssertionError, rf'Expected response status code "300", but got "{mock_response.status_code}".'
        ):
            self.assert_allowed_method(url, 'get', 300)

        mock_response.status_code = 405
        with self.assertRaisesRegex(AssertionError, r'Expected method "get" is not allowed.'):
            self.assert_allowed_method(url, 'get', 200)

    @patch('rest_framework.test.APIClient.get')
    def test_assert_not_allowed_methods(self, mock_client_get):
        mock_response = MagicMock(status_code=405)
        mock_client_get.return_value = mock_response
        url = '/'

        self.assert_not_allowed_methods(url, ['get'])  # not raise

        mock_response.status_code = 200
        with self.assertRaisesRegex(
            AssertionError, rf'Expected response status code "405", but got "{mock_response.status_code}".'
        ):
            self.assert_not_allowed_methods(url, ['get'])

    def test_assert_required_model_field(self):
        detail = 'This field cannot be blank'

        self.assert_required_model_field(TestModel, 'required_field', dict(required_field='test'), detail)  # not raise

        with self.assertRaisesRegex(AssertionError, r'This field "optional_field" is not required.'):
            self.assert_required_model_field(
                TestModel, 'optional_field', dict(required_field='test', optional_field='test'), detail
            )

    def test_assert_optional_model_field(self):
        self.assert_optional_model_field(TestModel, 'optional_field', dict(required_field='test'))  # not raise

        with self.assertRaisesRegex(
            AssertionError,
            r'This field "required_field" is not optional. It is required field.',
        ):
            self.assert_optional_model_field(TestModel, 'required_field', dict(required_field='test'))

        with self.assertRaisesRegex(
            AssertionError,
            'This field "default_field" is not optional. It has value by default.',
        ):
            self.assert_optional_model_field(TestModel, 'default_field', dict(required_field='test'))

    def test_assert_model_field_default_value(self):
        self.assert_model_field_default_value(TestModel, 'default_field', dict(required_field='test'), '1')
        self.assert_model_field_default_value(TestModel, 'default_true_field', dict(required_field='test'), True)
        self.assert_model_field_default_value(TestModel, 'default_false_field', dict(required_field='test'), False)

        with self.assertRaisesRegex(
            AssertionError,
            r'Expected default value "2", but got "1".',
        ):
            self.assert_model_field_default_value(TestModel, 'default_field', dict(required_field='test'), '2')

        with self.assertRaisesRegex(AssertionError, r'Expected default value "True", but got "False".'):
            self.assert_model_field_default_value(TestModel, 'default_false_field', dict(required_field='test'), True)

        with self.assertRaisesRegex(AssertionError, r'Expected default value "False", but got "True".'):
            self.assert_model_field_default_value(TestModel, 'default_true_field', dict(required_field='test'), False)

    def test_assert_validation_model_field(self):
        self.assert_validation_model_field(
            TestModel,
            dict(required_field='t'),
            detail='Ensure this value has at least 2 characters',
        )

        with self.assertRaises(AssertionError):
            self.assert_validation_model_field(
                TestModel,
                dict(required_field='test'),
                detail='Ensure this value has at least 2 characters',
            )
