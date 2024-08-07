from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from pydantic import ValidationError

from utils.tests.cases import ModelTestCase


class TestRelationModel(models.Model):
    class Meta:
        managed = False


class TestModel(models.Model):
    required = models.CharField(max_length=10)
    optional = models.CharField(max_length=20, null=True, blank=True)
    unique = models.CharField(max_length=1, unique=True)
    not_unique = models.CharField(max_length=1)
    decimal = models.DecimalField(max_digits=10, decimal_places=2)
    default = models.BooleanField(default=True)
    one_to_one = models.OneToOneField(to=TestRelationModel, on_delete=models.CASCADE, related_name='one_to_one')
    many_to_many = models.ManyToManyField(to=TestRelationModel, related_name='many_to_many')
    many_to_one = models.ForeignKey(to=TestRelationModel, on_delete=models.CASCADE)
    generic_one_to_many = GenericRelation(to=TestRelationModel)

    null_true = models.BooleanField(null=True)
    blank_true = models.BooleanField(blank=True)

    null_false = models.BooleanField(null=False, blank=True)
    blank_false = models.BooleanField(null=True, blank=False)

    class Meta:
        managed = False


class ModelTestCaseTest(ModelTestCase):
    def test_assert_required_fields(self):
        self.assert_required_fields(TestModel, ['required'])

        with self.assertRaisesRegex(
            AttributeError,
            r'The model "TestModel" has no field named "non_existent".',
        ):
            self.assert_required_fields(TestModel, ['non_existent'])

        with self.assertRaisesRegex(
            AssertionError,
            'The field "null_true" cannot be null.',
        ):
            self.assert_required_fields(TestModel, ['null_true'])

        with self.assertRaisesRegex(
            AssertionError,
            'The field "blank_true" cannot be blank.',
        ):
            self.assert_required_fields(TestModel, ['blank_true'])

    def test_assert_optional_fields(self):
        self.assert_optional_fields(TestModel, ['optional'])

        with self.assertRaisesRegex(
            AttributeError,
            r'The model "TestModel" has no field named "non_existent".',
        ):
            self.assert_optional_fields(TestModel, ['non_existent'])

        with self.assertRaisesRegex(
            AssertionError,
            'The field "null_false" must be null.',
        ):
            self.assert_optional_fields(TestModel, ['null_false'])

        with self.assertRaisesRegex(
            AssertionError,
            'The field "blank_false" must be blank.',
        ):
            self.assert_optional_fields(TestModel, ['blank_false'])

    def test_assert_fields_with_value_by_default(self):
        self.assert_fields_have_default_value(TestModel, dict(default=True))

        with self.assertRaisesRegex(
            AttributeError,
            r'The model "TestModel" has no field named "non_existent".',
        ):
            self.assert_fields_have_default_value(TestModel, dict(non_existent=True))

        with self.assertRaisesRegex(
            AssertionError,
            'The field "required" has no default value.',
        ):
            self.assert_fields_have_default_value(TestModel, dict(required=True))

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "default" must have "False" by default, but had "True".',
        ):
            self.assert_fields_have_default_value(TestModel, dict(default=False))

    def test_assert_fields_have_specified_max_length(self):
        self.assert_fields_have_specified_max_length(
            TestModel,
            dict(required=10, optional=20),
        )

        with self.assertRaisesRegex(
            AttributeError,
            r'The model "TestModel" has no field named "non_existent".',
        ):
            self.assert_fields_have_specified_max_length(TestModel, dict(non_existent=10))

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "required" must have "5" max length, but had "10".',
        ):
            self.assert_fields_have_specified_max_length(
                TestModel,
                dict(required=5),
            )

    def test_assert_fields_have_specified_relation(self):
        self.assert_fields_have_specified_relation(
            TestModel,
            [
                dict(name='one_to_one', to=TestRelationModel, relation='one_to_one', related_name='one_to_one'),
                dict(name='many_to_many', to=TestRelationModel, relation='many_to_many'),
                dict(name='many_to_one', to=TestRelationModel, relation='many_to_one'),
                dict(name='generic_one_to_many', to=TestRelationModel, relation='one_to_many'),
            ],
        )

        with self.assertRaisesRegex(
            AttributeError,
            r'The model "TestModel" has no field named "non_existent".',
        ):
            self.assert_fields_have_specified_relation(
                TestModel,
                [
                    dict(name='non_existent', to=TestRelationModel, relation='one_to_one', related_name='one_to_one'),
                ],
            )

        with self.assertRaises(ValidationError):
            self.assert_fields_have_specified_relation(
                TestModel,
                [
                    dict(),
                ],
            )

        with self.assertRaisesRegex(
            TypeError,
            r'The field "required" must be one of classes: "ForeignKey", "OneToOneField", "ManyToManyField".',
        ):
            self.assert_fields_have_specified_relation(
                TestModel,
                [
                    dict(name='required', to=TestRelationModel, relation='one_to_one', related_name='one_to_one'),
                ],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "one_to_one" must have "many_to_one" relation.',
        ):
            self.assert_fields_have_specified_relation(
                TestModel,
                [
                    dict(name='one_to_one', to=TestRelationModel, relation='many_to_one', related_name='one_to_one'),
                ],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "one_to_one" must is "TestModel", but was "TestRelationModel".',
        ):
            self.assert_fields_have_specified_relation(
                TestModel,
                [
                    dict(name='one_to_one', to=TestModel, relation='one_to_one', related_name='one_to_one'),
                ],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "one_to_one" must have "many_to_many" related name", but had "one_to_one".',
        ):
            self.assert_fields_have_specified_relation(
                TestModel,
                [
                    dict(name='one_to_one', to=TestRelationModel, relation='one_to_one', related_name='many_to_many'),
                ],
            )

    def test_assert_decimal_fields(self):
        self.assert_decimal_fields(TestModel, [dict(name='decimal', max_digits=10, decimal_places=2)])

        with self.assertRaisesRegex(
            AttributeError,
            r'The model "TestModel" has no field named "non_existent".',
        ):
            self.assert_decimal_fields(
                TestModel,
                [dict(name='non_existent', max_digits=10, decimal_places=2)],
            )

        with self.assertRaisesRegex(
            TypeError,
            r'The field "required" must be class named "DecimalField".',
        ):
            self.assert_decimal_fields(
                TestModel,
                [dict(name='required', max_digits=10, decimal_places=2)],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "decimal" must have "12" max digits, but had "10".',
        ):
            self.assert_decimal_fields(
                TestModel,
                [dict(name='decimal', max_digits=12, decimal_places=2)],
            )

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "decimal" must have "4" decimal places, but had "2".',
        ):
            self.assert_decimal_fields(
                TestModel,
                [dict(name='decimal', max_digits=10, decimal_places=4)],
            )

    def test_(self):
        self.assert_unique_fields(TestModel, ['unique'])  # not raise

        with self.assertRaisesRegex(
            AssertionError,
            r'The field "not_unique" must be unique.',
        ):
            self.assert_unique_fields(TestModel, ['not_unique'])
