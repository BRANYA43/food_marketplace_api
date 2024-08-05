from typing import Type, Any

from rest_framework.fields import empty
from rest_framework.serializers import Serializer, ModelSerializer

from utils.tests.cases import BaseTestCase


class SerializerTestCase(BaseTestCase):
    @staticmethod
    def __get_field(serializer, field_name: str):
        try:
            return serializer().fields[field_name]
        except KeyError:
            raise AttributeError(f'The serializer "{serializer.__name__}" have no field named "{field_name}".')

    def assert_required_fields(
        self, serializer: Type[Serializer], fields: list[str], null: bool = None, blank: bool = None
    ):
        for field_name in fields:
            field = self.__get_field(serializer, field_name)
            self.assertTrue(
                field.required,
                msg=f'The field "{field_name}" must be required.',
            )
            if null is not None:
                self.assertEqual(
                    field.allow_null,
                    null,
                    msg=f'The field "{field_name}" must have "allow_null" as "{null}".',
                )
            if blank is not None:
                self.assertEqual(
                    field.allow_blank,
                    blank,
                    msg=f'The field "{field_name}" must have "allow_blank" as "{blank}".',
                )

    def assert_optional_fields(
        self, serializer: Type[Serializer], fields: list[str], null: bool = None, blank: bool = None
    ):
        for field_name in fields:
            field = self.__get_field(serializer, field_name)
            self.assertFalse(
                field.required,
                msg=f'The field "{field_name}" must be not required.',
            )
            if null is not None:
                self.assertEqual(
                    field.allow_null,
                    null,
                    msg=f'The field "{field_name}" must have "allow_null" as "{null}".',
                )
            if blank is not None:
                self.assertEqual(
                    field.allow_blank,
                    blank,
                    msg=f'The field "{field_name}" must have "allow_blank" as "{blank}".',
                )

    def assert_fields_have_default_value(self, serializer: Type[Serializer], fields: dict[str, Any]):
        for field_name, expected_value in fields.items():
            field = self.__get_field(serializer, field_name)
            if field.default is empty:
                raise AssertionError(f'The field "{field_name}" have no default value.')
            self.assertEqual(
                field.default,
                expected_value,
                msg=f'The field "{field_name}" must have "{expected_value}" by default, but had "{field.default}".',
            )

    def assert_fields_have_specified_min_length(self, serializer: Type[Serializer], fields: dict[str, int]):
        for field_name, expected_value in fields.items():
            field = self.__get_field(serializer, field_name)
            self.assertEqual(
                field.min_length,
                expected_value,
                msg=f'The field "{field_name}" must have "{expected_value}" min length, but had "{field.min_length}".',
            )

    def assert_fields_have_specified_max_length(self, serializer: Type[Serializer], fields: dict[str, int]):
        for field_name, expected_value in fields.items():
            field = self.__get_field(serializer, field_name)
            self.assertEqual(
                field.max_length,
                expected_value,
                msg=f'The field "{field_name}" must have "{expected_value}" max length, but had "{field.max_length}".',
            )

    def assert_fields_are_read_only(self, serializer: Type[Serializer], fields: list[str]):
        for field_name in fields:
            field = self.__get_field(serializer, field_name)
            self.assertTrue(
                field.read_only,
                msg=f'The field "{field_name}" must be read only.',
            )

    def assert_fields_are_write_only(self, serializer: Type[Serializer], fields: list[str]):
        for field_name in fields:
            field = self.__get_field(serializer, field_name)
            self.assertTrue(
                field.write_only,
                msg=f'The field "{field_name}" must be write only.',
            )

    @staticmethod
    def create_serializer(
        serializer: Type[Serializer],
        input_data: dict[str, Any] | list[dict[str, Any]] = empty,
        save=False,
        **extra_params,
    ) -> Serializer | ModelSerializer:
        serializer = serializer(data=input_data, **extra_params)

        if not isinstance(input_data, empty):
            serializer.is_valid(raise_exception=True)

        if save:
            serializer.save()

        return serializer

    def assert_output_serializer_data(
        self,
        serializer: Type[Serializer],
        input_data: dict[str, Any] | list[dict[str, Any]],
        output_data: dict[str, Any] | list[dict[str, Any]],
        save=False,
        **extra_params,
    ):
        serializer = self.create_serializer(serializer, input_data, save, **extra_params)

        self.assertEqual(serializer.data, output_data)
