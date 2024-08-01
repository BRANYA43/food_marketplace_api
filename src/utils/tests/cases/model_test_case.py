from typing import Any, Literal, Type

from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Model, ForeignKey, OneToOneField, ManyToManyField, Field
from django.db.models.fields import NOT_PROVIDED, DecimalField
from pydantic import BaseModel

from utils.tests.cases.base_test_case import BaseTestCase


class ModelTestCase(BaseTestCase):
    class RelationField(BaseModel):
        name: str
        to: Type[Model]
        relation: Literal['one_to_one', 'many_to_many', 'one_to_many', 'many_to_one']
        related_name: str | None = None

    class DecimalField(BaseModel):
        name: str
        max_digits: int
        decimal_places: int

    @staticmethod
    def __get_field(model: Type[Model], field_name: str) -> Type[Field]:
        try:
            field = getattr(model, field_name).field
        except AttributeError:
            raise AttributeError(f'The model "{model.__name__}" has no field named "{field_name}".')
        return field

    def assert_required_fields(self, model: Type[Model], fields: list[str]):
        for field_name in fields:
            field = self.__get_field(model, field_name)
            self.assertFalse(
                getattr(field, 'null'),
                msg=f'The field "{field_name}" cannot be null.',
            )
            self.assertFalse(getattr(field, 'blank'), msg=f'The field "{field_name}" cannot be blank.')

    def assert_optional_fields(self, model: Type[Model], fields: list[str]):
        for field_name in fields:
            field = self.__get_field(model, field_name)
            self.assertTrue(
                getattr(field, 'null'),
                msg=f'The field "{field_name}" must be null.',
            )
            self.assertTrue(
                getattr(field, 'blank'),
                msg=f'The field "{field_name}" must be blank.',
            )

    def assert_fields_with_value_by_default(self, model: Type[Model], fields: dict[str, Any]):
        for field_name, expected_value in fields.items():
            field = self.__get_field(model, field_name)
            got_value = getattr(field, 'default')
            if got_value is NOT_PROVIDED:
                raise AssertionError(f'The field "{field_name}" has no default value.')
            self.assertEqual(
                got_value,
                expected_value,
                msg=f'The field "{field_name}" must have "{expected_value}" by default, but had "{got_value}".',
            )

    def assert_fields_have_specified_max_length(self, model: Type[Model], fields: dict[str, int]):
        for field_name, expected_value in fields.items():
            field = self.__get_field(model, field_name)
            got_value = getattr(field, 'max_length')
            self.assertEqual(
                got_value,
                expected_value,
                msg=f'The field "{field_name}" must have "{expected_value}" max length, but had "{got_value}".',
            )

    def assert_fields_have_specified_relation(self, model: Type[Model], fields: list[RelationField | dict]):
        for field_data in fields:
            field_data = self.RelationField(**field_data)  # type: ignore
            field = self.__get_field(model, field_data.name)
            if not isinstance(field, (ForeignKey, OneToOneField, ManyToManyField, GenericRelation)):
                raise TypeError(
                    f'The field "{field_data.name}" must be one of classes: "ForeignKey", '
                    f'"OneToOneField", "ManyToManyField", "GenericRelation".'
                )
            got_relation = getattr(field, field_data.relation)
            self.assertTrue(
                got_relation,
                msg=f'The field "{field_data.name}" must have "{field_data.relation}" relation.',
            )
            got_related_model = field.related_model
            self.assertIs(
                got_related_model,
                field_data.to,
                msg=f'The field "{field_data.name}" must is "{field_data.to.__name__}", but was '
                f'"{got_related_model.__name__}".',
            )

            if field_data.related_name:
                got_related_name = field.related_query_name()
                self.assertEqual(
                    got_related_name,
                    field_data.related_name,
                    msg=f'The field "{field_data.name}" must have "{field_data.related_name}" related name", but had '
                    f'"{got_related_name}".',
                )

    def assert_decimal_fields(self, model: Type[Model], fields: list[DecimalField | dict]):
        for field_data in fields:
            field_data = self.DecimalField(**field_data)  # type: ignore
            field = self.__get_field(model, field_data.name)
            if not isinstance(field, DecimalField):
                raise TypeError(
                    f'The field "{field_data.name}" must be class named "DecimalField".',
                )
            got_max_digits = field.max_digits
            self.assertEqual(
                got_max_digits,
                field_data.max_digits,
                msg=f'The field "{field_data.name}" must have "{field_data.max_digits}" max digits, but had "{got_max_digits}".',
            )
            got_decimal_places = field.decimal_places
            self.assertEqual(
                got_decimal_places,
                field_data.decimal_places,
                msg=f'The field "{field_data.name}" must have "{field_data.decimal_places}" decimal places, but had "{got_decimal_places}".',
            )
