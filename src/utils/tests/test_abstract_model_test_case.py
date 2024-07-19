from django.db import models

from utils.tests import AbstractModelTestCase


class TestModelMixin(models.Model):
    field = models.BooleanField(default=True)

    class Meta:
        abstract = True


class AbstractModelTestCaseTest(AbstractModelTestCase):
    abstract_model = TestModelMixin

    def test_model_inherits_abstract_model(self):
        self.assert_is_subclass(self.model, self.abstract_model)

    def test_model_is_created(self):
        instance = self.model.objects.create()
        self.assertTrue(instance.field)
