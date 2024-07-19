from unittest.mock import MagicMock, patch

from django.core.validators import MinLengthValidator
from django.db import models
from rest_framework import serializers

from utils.tests import ApiTestCase


class TestSerializer(serializers.Serializer):
    write_only_field = serializers.CharField(write_only=True, required=False)
    optional_field = serializers.CharField(required=False)
    default_field = serializers.CharField(default='default')
    required_field = serializers.CharField()
    read_only_field = serializers.ReadOnlyField()

    class Meta:
        fields = '__all__'


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

    def test_assert_required_model_fields(self):
        self.assert_required_model_fields(TestModel, dict(required_field='test'), ['required_field'])  # not raise
        with self.assertRaisesRegex(AssertionError, r'This field "optional_field" is not required.'):
            self.assert_required_model_fields(
                TestModel,
                dict(required_field='test', optional_field='test'),
                ['optional_field'],
            )

    def test_assert_optional_model_fields(self):
        self.assert_optional_model_fields(
            TestModel,
            dict(required_field='test'),
            ['optional_field'],
        )  # not raise
        self.assert_optional_model_fields(
            TestModel,
            dict(required_field='test', optional_field='test'),
            ['optional_field'],
        )  # not raise

        with self.assertRaisesRegex(AssertionError, r'This field "required_field" is not optional. It is required.'):
            self.assert_optional_model_fields(
                TestModel,
                dict(required_field='test', optional_field='test'),
                ['required_field'],
            )

        with self.assertRaisesRegex(
            AssertionError, r'This field "default_field" is not optional. It is set by default.'
        ):
            self.assert_optional_model_fields(
                TestModel,
                dict(required_field='test'),
                ['default_field'],
            )

    def test_assert_set_model_fields_by_default(self):
        self.assert_set_model_fields_by_default(
            TestModel,
            dict(required_field='test'),
            dict(default_field='1'),
        )  # not raise

        self.assert_set_model_fields_by_default(
            TestModel,
            dict(required_field='test', default_field='2'),
            dict(default_field='1'),
        )  # not raise

        with self.assertRaisesRegex(AssertionError, r'This field "required_field" have no a default value.'):
            self.assert_set_model_fields_by_default(
                TestModel,
                dict(required_field='test'),
                dict(required_field='test'),
            )

        with self.assertRaisesRegex(
            AssertionError, r'This field "default_field" is not set by default as "2". \(There set 1.\)'
        ):
            self.assert_set_model_fields_by_default(
                TestModel,
                dict(required_field='test'),
                dict(default_field='2'),
            )

    def test_assert_write_only_serializer_fields(self):
        self.assert_write_only_serializer_fields(
            TestSerializer,
            dict(write_only_field='write', required_field='required'),
            ['write_only_field'],
        )  # not raise

        with self.assertRaisesRegex(AssertionError, r'This field "required_field" is not write only.'):
            self.assert_write_only_serializer_fields(
                TestSerializer,
                dict(required_field='required'),
                ['required_field'],
            )

    def test_assert_required_serializer_fields(self):
        self.assert_required_serializer_fields(
            TestSerializer, dict(required_field='required'), ['required_field']
        )  # not raise

        with self.assertRaisesRegex(AssertionError, r'This field "optional_field" is not required.'):
            self.assert_required_serializer_fields(
                TestSerializer,
                dict(required_field='required', optional_field='optional'),
                ['optional_field'],
            )

    def test_assert_optional_serializer_fields(self):
        self.assert_optional_serializer_fields(TestSerializer, ['optional_field'])  # not raise

        with self.assertRaisesRegex(
            AssertionError,
            r'This field "required_field" is not optional. It is required.',
        ):
            self.assert_optional_serializer_fields(TestSerializer, ['required_field'])
