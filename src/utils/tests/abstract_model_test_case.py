from typing import Any

from django.db import connection
from django.db.models.base import ModelBase

from utils.tests import ApiTestCase


class AbstractModelTestCase(ApiTestCase):
    abstract_model: Any = None
    model: Any = None

    @classmethod
    def setUpClass(cls):
        cls.model = ModelBase(
            'TestModel' + cls.abstract_model.__name__,
            (cls.abstract_model,),
            {'__module__': cls.abstract_model.__module__},
        )

        with connection.schema_editor() as editor:
            editor.create_model(cls.model)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        with connection.schema_editor() as editor:
            editor.delete_model(cls.model)

        connection.close()
