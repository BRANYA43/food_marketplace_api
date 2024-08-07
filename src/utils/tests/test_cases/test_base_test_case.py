from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from utils.tests.cases import BaseTestCase


class TestSerializerForCreate(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def save(self, **kwargs):
        raise NotImplementedError('.save() method was called.')


class BaseTestCaseTest(BaseTestCase):
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

    def test_create_serializer(self):
        serializer = self.create_serializer(
            TestSerializerForCreate,
            dict(username='username', password='123'),
            initial=dict(username='initial username'),
        )

        self.assertIsInstance(serializer, serializers.Serializer)
        self.assertEqual(serializer.data, dict(username='username'))
        # creator gives arguments to serializer
        self.assertEqual(serializer.initial, dict(username='initial username'))

        with self.assertRaisesRegex(ValidationError, r'password.+required'):
            self.create_serializer(
                TestSerializerForCreate,
                dict(username='username'),
            )

        with self.assertRaisesRegex(NotImplementedError, r'.save\(\) method was called.'):
            self.create_serializer(
                TestSerializerForCreate,
                dict(username='username', password='123'),
                save=True,
            )
