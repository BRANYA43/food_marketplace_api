from django.contrib.auth import get_user_model
from rest_framework import serializers

from utils import models
from utils.serializers import mixins
from utils.tests import ApiTestCase

User = get_user_model()


class AddressMixinTest(ApiTestCase):
    user_model = User
    address_model = models.Address

    class TestSerializer(mixins.AddressCreateUpdateMixin, serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('email', 'password', 'address')

    def setUp(self) -> None:
        self.serializer_class = self.TestSerializer
        self.create_address_data = dict(
            city='city',
            street='street',
            number='number',
        )
        self.update_address_data = dict(
            number='new number',
        )
        self.create_user_data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
        )
        self.update_user_data = dict(
            email='new.email@test.com',
        )

    def test_expected_fields_are_optional(self):
        self.assert_optional_serializer_fields(self.serializer_class, ['address'])

    def test_mixin_creates_content_obj_without_address(self):
        self.assertEqual(self.user_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

        serializer = self.serializer_class(data=self.create_user_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(self.user_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 0)

        user = self.user_model.objects.first()

        self.assertEqual(user.email, self.create_user_data['email'])
        self.assertEqual(user.password, self.create_user_data['password'])

    def test_mixin_creates_content_obj_with_address(self):
        self.create_user_data['address'] = self.create_address_data

        self.assertEqual(self.user_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

        serializer = self.serializer_class(data=self.create_user_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(self.user_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 1)

        user = self.user_model.objects.first()

        self.assertEqual(user.email, self.create_user_data['email'])
        self.assertEqual(user.password, self.create_user_data['password'])

        address = self.address_model.objects.first()

        self.assertEqual(address.content_obj.id, user.id)
        self.assertEqual(address.city, self.create_address_data['city'])
        self.assertEqual(address.street, self.create_address_data['street'])
        self.assertEqual(address.number, self.create_address_data['number'])

    def test_mixin_updates_content_obj_without_address(self):
        user = self.create_test_user()

        self.assertNotEqual(user.email, self.update_user_data['email'])
        self.assertEqual(self.address_model.objects.count(), 0)

        serializer = self.serializer_class(user, self.update_user_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(self.address_model.objects.count(), 0)
        self.assertEqual(user.email, self.update_user_data['email'])

    def test_mixin_updates_content_obj_with_address(self):
        self.update_user_data['address'] = self.update_address_data

        user = self.create_test_user()
        address = self.create_test_address(user)

        self.assertNotEqual(user.email, self.update_user_data['email'])
        self.assertNotEqual(address.number, self.update_address_data['number'])

        serializer = self.serializer_class(user, self.update_user_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(user.email, self.update_user_data['email'])

        address.refresh_from_db()

        self.assertEqual(address.number, self.update_address_data['number'])

    def test_mixin_updates_content_obj_and_create_address(self):
        self.update_user_data['address'] = self.create_address_data

        user = self.create_test_user()

        self.assertNotEqual(user.email, self.update_user_data['email'])
        self.assertEqual(self.address_model.objects.count(), 0)

        serializer = self.serializer_class(user, self.update_user_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        self.assertEqual(self.address_model.objects.count(), 1)
        self.assertEqual(user.email, self.update_user_data['email'])

        address = self.address_model.objects.first()

        self.assertEqual(address.content_obj.id, user.id)
        self.assertEqual(address.city, self.create_address_data['city'])
        self.assertEqual(address.street, self.create_address_data['street'])
        self.assertEqual(address.number, self.create_address_data['number'])
