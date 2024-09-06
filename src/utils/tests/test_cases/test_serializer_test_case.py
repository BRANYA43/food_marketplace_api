from rest_framework import serializers

from utils.tests.cases import SerializerTestCase


class TestSerializer(serializers.Serializer):
    required = serializers.CharField(required=True)
    required_null_blank = serializers.CharField(required=True, allow_null=True, allow_blank=True)

    optional = serializers.CharField(required=False)
    optional_null_blank = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    length = serializers.CharField(max_length=100, min_length=10)

    default = serializers.BooleanField(default=True)
    not_default = serializers.ReadOnlyField()

    readonly = serializers.ReadOnlyField()
    not_readonly = serializers.BooleanField()

    writeonly = serializers.BooleanField(write_only=True)
    not_writeonly = serializers.BooleanField()


class TestSerializerForCreate(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def save(self, **kwargs):
        raise NotImplementedError('.save() method was called.')


class SerializerTestCaseTest(SerializerTestCase):
    def test_assert_required_fields(self):
        self.assert_required_fields(TestSerializer, ['required'])
        self.assert_required_fields(TestSerializer, ['required_null_blank'], null=True, blank=True)

        with self.assertRaisesRegex(
            AttributeError,
            r'The serializer "TestSerializer" have no field named "non_existent".',
        ):
            self.assert_required_fields(
                TestSerializer,
                ['non_existent'],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "optional" must be required.',
        ):
            self.assert_required_fields(
                TestSerializer,
                ['optional'],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "required_null_blank" must have "allow_null" as "False".',
        ):
            self.assert_required_fields(
                TestSerializer,
                ['required_null_blank'],
                null=False,
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "required_null_blank" must have "allow_blank" as "False".',
        ):
            self.assert_required_fields(
                TestSerializer,
                ['required_null_blank'],
                blank=False,
            )

    def test_assert_optional_fields(self):
        self.assert_optional_fields(TestSerializer, ['optional'])
        self.assert_optional_fields(TestSerializer, ['optional_null_blank'], null=True, blank=True)

        with self.assertRaisesRegex(
            AttributeError,
            r'The serializer "TestSerializer" have no field named "non_existent".',
        ):
            self.assert_optional_fields(
                TestSerializer,
                ['non_existent'],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "required" must be not required.',
        ):
            self.assert_optional_fields(
                TestSerializer,
                ['required'],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "optional_null_blank" must have "allow_null" as "False".',
        ):
            self.assert_optional_fields(
                TestSerializer,
                ['optional_null_blank'],
                null=False,
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "optional_null_blank" must have "allow_blank" as "False".',
        ):
            self.assert_optional_fields(
                TestSerializer,
                ['optional_null_blank'],
                blank=False,
            )

    def test_assert_fields_have_default_value(self):
        self.assert_fields_have_default_value(
            TestSerializer,
            dict(default=True),
        )

        with self.assertRaisesRegex(
            AttributeError,
            r'The serializer "TestSerializer" have no field named "non_existent".',
        ):
            self.assert_fields_have_default_value(
                TestSerializer,
                dict(non_existent=True),
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "not_default" have no default value.',
        ):
            self.assert_fields_have_default_value(
                TestSerializer,
                dict(not_default=True),
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "default" must have "False" by default, but had "True".',
        ):
            self.assert_fields_have_default_value(
                TestSerializer,
                dict(default=False),
            )

    def test_assert_fields_have_specified_max_length(self):
        self.assert_fields_have_specified_max_length(
            TestSerializer,
            dict(length=100),
        )

        with self.assertRaisesRegex(
            AttributeError,
            r'The serializer "TestSerializer" have no field named "non_existent".',
        ):
            self.assert_fields_have_specified_max_length(
                TestSerializer,
                dict(non_existent=100),
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "length" must have "0" max length, but had "100".',
        ):
            self.assert_fields_have_specified_max_length(
                TestSerializer,
                dict(length=0),
            )

    def test_assert_fields_have_specified_min_length(self):
        self.assert_fields_have_specified_min_length(
            TestSerializer,
            dict(length=10),
        )

        with self.assertRaisesRegex(
            AttributeError,
            r'The serializer "TestSerializer" have no field named "non_existent".',
        ):
            self.assert_fields_have_specified_min_length(
                TestSerializer,
                dict(non_existent=10),
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "length" must have "0" min length, but had "10".',
        ):
            self.assert_fields_have_specified_min_length(
                TestSerializer,
                dict(length=0),
            )

    def test_assert_fields_are_read_only(self):
        self.assert_fields_are_read_only(
            TestSerializer,
            ['readonly'],
        )

        with self.assertRaisesRegex(
            AttributeError,
            r'The serializer "TestSerializer" have no field named "non_existent".',
        ):
            self.assert_fields_are_read_only(
                TestSerializer,
                ['non_existent'],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "not_readonly" must be read only.',
        ):
            self.assert_fields_are_read_only(
                TestSerializer,
                ['not_readonly'],
            )

    def test_assert_fields_are_write_only(self):
        self.assert_fields_are_write_only(
            TestSerializer,
            ['writeonly'],
        )

        with self.assertRaisesRegex(
            AttributeError,
            r'The serializer "TestSerializer" have no field named "non_existent".',
        ):
            self.assert_fields_are_write_only(
                TestSerializer,
                ['non_existent'],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "not_writeonly" must be write only.',
        ):
            self.assert_fields_are_write_only(
                TestSerializer,
                ['not_writeonly'],
            )

    def test_assert_output_serializer_data(self):
        self.assert_output_serializer_data(
            TestSerializerForCreate,
            input_data=dict(username='username', password='123'),
            output_data=dict(username='username'),
        )

        with self.assertRaisesRegex(NotImplementedError, r'.save\(\) method was called.'):
            self.create_serializer_deprecated(
                TestSerializerForCreate,
                input_data=dict(username='username', password='123'),
                save=True,
            )
