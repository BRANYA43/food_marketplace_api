from django.contrib.auth import get_user_model
from rest_framework import serializers

from utils import models
from utils.serializers import mixins
from utils.tests.cases import BaseTestCase

User = get_user_model()


class TestSerializer(mixins.AddressCreateUpdateMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'address')


class AddressMixinTest(BaseTestCase):
    serializer_class = TestSerializer
    user_model = User
    address_model = models.Address

    def setUp(self) -> None:
        self.input_address_data = dict(
            city='new city',
            street='new street',
            number='new number',
        )
        self.create_input_data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
        )
        self.update_input_data = dict(
            email='new.email@test.com',
        )

    def test_mixin_creates_content_obj_without_address(self):
        self.assertEqual(self.user_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

        self.create_serializer(
            self.serializer_class,
            data=self.create_input_data,
            save=True,
        )

        self.assertEqual(self.user_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 0)

        user = self.user_model.objects.first()

        self.assert_model_instance(user, self.create_input_data)

    def test_mixin_creates_content_obj_with_address(self):
        self.assertEqual(self.user_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

        data = dict(**self.create_input_data, address=self.input_address_data)
        self.create_serializer(
            self.serializer_class,
            data=data,
            save=True,
        )

        self.assertEqual(self.user_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 1)

        user = self.user_model.objects.first()
        address = self.address_model.objects.first()

        self.assert_model_instance(user, self.create_input_data)
        self.assertEqual(address.content_obj.id, user.id)
        self.assert_model_instance(address, self.input_address_data)

    def test_mixin_updates_content_obj_without_address(self):
        user = self.create_test_user()

        self.assert_model_instance(user, self.update_input_data, equal=False)
        self.assertEqual(self.address_model.objects.count(), 0)

        self.create_serializer(
            self.serializer_class,
            data=self.update_input_data,
            instance=user,
            save=True,
            partial=True,
        )

        self.assert_model_instance(user, self.update_input_data)
        self.assertEqual(self.address_model.objects.count(), 0)

    def test_mixin_updates_content_obj_with_address(self):
        user = self.create_test_user()
        address = self.create_test_address(user)

        self.assert_model_instance(user, self.update_input_data, equal=False)
        self.assert_model_instance(address, self.input_address_data, equal=False)

        data = dict(**self.update_input_data, address=self.input_address_data)
        self.create_serializer(
            self.serializer_class,
            data=data,
            instance=user,
            save=True,
            partial=True,
        )

        address.refresh_from_db()

        self.assert_model_instance(user, self.update_input_data)
        self.assert_model_instance(address, self.input_address_data)

    def test_mixin_updates_content_obj_and_create_address(self):
        user = self.create_test_user()

        self.assert_model_instance(user, self.update_input_data, equal=False)
        self.assertEqual(self.address_model.objects.count(), 0)

        data = dict(**self.update_input_data, address=self.input_address_data)
        self.create_serializer(
            self.serializer_class,
            data=data,
            instance=user,
            save=True,
            partial=True,
        )

        address = self.address_model.objects.first()

        self.assertEqual(self.address_model.objects.count(), 1)
        self.assert_model_instance(user, self.update_input_data)
        self.assert_model_instance(address, self.input_address_data)

    def test_mixin_returns_expected_data_without_address(self):
        self.assert_serializer_output_data(
            self.serializer_class,
            data=self.create_input_data,
            expected_data=dict(**self.create_input_data, address={}),
            save=True,
        )

    def test_mixin_returns_expected_data_with_address(self):
        self.assert_serializer_output_data(
            self.serializer_class,
            data=dict(**self.create_input_data, address=self.input_address_data),
            expected_data=dict(**self.create_input_data, address=self.input_address_data),
            save=True,
        )
