from unittest.mock import patch, MagicMock

from rest_framework import serializers

from utils.tests.cases import BaseTestCase


class TestSerializerForCreate(serializers.Serializer):
    username = serializers.CharField()

    def save(self, **kwargs):
        return NotImplementedError


class BaseTestCaseTest(BaseTestCase):
    def setUp(self):
        self.serializer_data = dict(username='username')

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

    def test_create_serializer_without_data(self):
        serializer = self.create_serializer(TestSerializerForCreate)

        self.assertIsInstance(serializer, TestSerializerForCreate)

    def test_create_serializer_with_data(self):
        serializer = self.create_serializer(
            TestSerializerForCreate,
            data=self.serializer_data,
        )

        self.assertEqual(serializer.data, self.serializer_data)

    @patch.object(TestSerializerForCreate, 'is_valid')
    def test_serializer_creating_calls_is_valid_method_if_data_is_supplied(self, mock_is_valid: MagicMock):
        self.create_serializer(
            TestSerializerForCreate,
            data=self.serializer_data,
        )
        mock_is_valid.assert_called()

    @patch.object(TestSerializerForCreate, 'save')
    def test_serializer_creating_calls_save_method_if_save_is_true(self, mock_save: MagicMock):
        self.create_serializer(
            TestSerializerForCreate,
            data=self.serializer_data,
            save=True,
        )
        mock_save.assert_called()
