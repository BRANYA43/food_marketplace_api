from decimal import Decimal

from rest_framework import status
from rest_framework.reverse import reverse

from catalogs.models import Advert
from catalogs.serializers import (
    AdvertListSerializer,
    AdvertCreateSerializer,
    AdvertUpdateSerializer,
    AdvertRetrieveSerializer,
)
from utils.models import Address
from utils.tests.cases import BaseTestCase

LIST_URL = 'advert-list'
DETAIL_URL = 'advert-detail'


class AdvertListViewTest(BaseTestCase):
    url = reverse(LIST_URL)
    serializer_class = AdvertListSerializer

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)

    def test_view_is_available_to_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assert_response(response, status.HTTP_200_OK)

    def test_view_returns_expected_data(self):
        serializer = self.create_serializer_deprecated(self.serializer_class, instance=[self.advert], many=True)
        response = self.client.get(self.url)
        self.assert_response(
            response,
            status.HTTP_200_OK,
            expected_data=serializer.data,
            is_paginated=True,
        )


class AdvertRetrieveViewTest(BaseTestCase):
    serializer_class = AdvertRetrieveSerializer
    advert_model = Advert
    address_model = Address

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)
        self.url = reverse(DETAIL_URL, [self.advert.pk])

    def test_view_is_available_to_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assert_response(response, status.HTTP_200_OK)

    def test_view_returns_expected_data(self):
        serializer = self.create_serializer_deprecated(self.serializer_class, instance=self.advert)
        response = self.client.get(self.url)
        self.assert_response(
            response,
            status.HTTP_200_OK,
            expected_data=serializer.data,
        )


class AdvertCreateViewTest(BaseTestCase):
    url = reverse(LIST_URL)
    serializer_class = AdvertCreateSerializer
    advert_model = Advert
    address_model = Address

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.input_data = dict(
            owner=self.owner.pk,
            category=self.category.pk,
            name='name',
            price=Decimal('100.00'),
        )
        self.address_input_data = dict(
            city='city',
            street='street',
            number='number',
        )
        self.login_user_by_token(self.owner)

    def test_view_isnt_available_to_unauthenticated_user(self):
        self.logout_user_by_token(self.owner)

        response = self.client.post(self.url, data=self.input_data)

        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_available_to_authenticated_user(self):
        response = self.client.post(self.url, data=self.input_data)

        self.assert_response(response, status.HTTP_201_CREATED)

    def test_view_creates_advert_without_address(self):
        self.assertEqual(self.advert_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

        response = self.client.post(self.url, data=self.input_data)

        self.assertEqual(self.advert_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 0)
        self.assert_response(response, status.HTTP_201_CREATED)

        advert = self.advert_model.objects.first()
        self.assert_model_instance(advert, self.input_data)

    def test_view_creates_advert_with_address(self):
        self.assertEqual(self.advert_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

        data = dict(**self.input_data, address=self.address_input_data)
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(self.advert_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 1)
        self.assert_response(response, status.HTTP_201_CREATED)

        advert = self.advert_model.objects.first()
        self.assert_model_instance(advert, self.input_data)

        address = advert.address.first()
        self.assert_model_instance(address, self.address_input_data)

    def test_view_returns_expected_data_without_address(self):
        response = self.client.post(self.url, data=self.input_data)

        advert = self.advert_model.objects.first()
        serializer = self.create_serializer_deprecated(self.serializer_class, instance=advert)
        self.assert_response(response, status.HTTP_201_CREATED, expected_data=serializer.data)

    def test_view_returns_expected_data_with_address(self):
        data = dict(**self.input_data, address=self.address_input_data)
        response = self.client.post(self.url, data=data, format='json')

        advert = self.advert_model.objects.first()
        serializer = self.create_serializer_deprecated(self.serializer_class, instance=advert)
        self.assert_response(response, status.HTTP_201_CREATED, expected_data=serializer.data)


class AdvertUpdateViewTest(BaseTestCase):
    serializer_class = AdvertUpdateSerializer
    advert_model = Advert
    address_model = Address

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)
        self.url = reverse('advert-detail', [self.advert.pk])
        self.input_data = dict(
            name='new name',
        )
        self.address_input_data = dict(
            city='new city',
            street='new street',
            number='new number',
        )

        self.login_user_by_token(self.owner)

    def test_view_isnt_available_to_unauthenticated_user(self):
        self.logout_user_by_token(self.owner)

        response = self.client.patch(self.url, self.input_data)

        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_available_to_authenticated_owner(self):
        response = self.client.patch(self.url, self.input_data)

        self.assert_response(response, status.HTTP_200_OK)

    def test_view_isnt_available_to_not_owner(self):
        not_owner = self.create_test_user(email='not.owner@test.com')
        self.login_user_by_token(not_owner)

        response = self.client.patch(self.url, self.input_data)

        self.assert_response(response, status.HTTP_403_FORBIDDEN)

    def test_view_updates_advert_without_address(self):
        self.assert_model_instance(self.advert, self.input_data, equal=False)

        response = self.client.patch(self.url, self.input_data)

        self.advert.refresh_from_db()

        self.assert_response(response, status.HTTP_200_OK)
        self.assert_model_instance(self.advert, self.input_data)

    def test_view_updates_advert_with_address(self):
        address = self.create_test_address(self.advert)

        self.assert_model_instance(self.advert, self.input_data, equal=False)
        self.assert_model_instance(address, self.address_input_data, equal=False)

        data = dict(**self.input_data, address=self.address_input_data)
        response = self.client.patch(self.url, data, format='json')

        self.advert.refresh_from_db()
        address.refresh_from_db()

        self.assert_response(response, status.HTTP_200_OK)
        self.assert_model_instance(self.advert, self.input_data)
        self.assert_model_instance(address, self.address_input_data)

    def test_view_updates_advert_and_create_address(self):
        self.assertEqual(self.address_model.objects.count(), 0)

        self.assert_model_instance(self.advert, self.input_data, equal=False)

        data = dict(**self.input_data, address=self.address_input_data)
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(self.address_model.objects.count(), 1)

        self.advert.refresh_from_db()
        address = self.advert.address.first()

        self.assert_response(response, status.HTTP_200_OK)
        self.assert_model_instance(self.advert, self.input_data)
        self.assert_model_instance(address, self.address_input_data)

    def test_view_returns_expected_data_without_address(self):
        response = self.client.patch(self.url, self.input_data)

        self.advert.refresh_from_db()
        serializer = self.create_serializer_deprecated(self.serializer_class, instance=self.advert)

        self.assert_response(response, status.HTTP_200_OK, expected_data=serializer.data)

    def test_view_returns_expected_data_with_address(self):
        self.create_test_address(self.advert)

        response = self.client.patch(self.url, self.input_data)

        self.advert.refresh_from_db()
        serializer = self.create_serializer_deprecated(self.serializer_class, instance=self.advert)

        self.assert_response(response, status.HTTP_200_OK, expected_data=serializer.data)


class AdvertDeleteViewTest(BaseTestCase):
    advert_model = Advert
    address_model = Address

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)
        self.url = reverse('advert-detail', [self.advert.pk])

        self.login_user_by_token(self.owner)

    def test_view_isnt_available_to_unauthenticated_user(self):
        self.logout_user_by_token(self.owner)

        response = self.client.delete(self.url)

        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_available_to_authenticated_owner(self):
        response = self.client.delete(self.url)

        self.assert_response(response, status.HTTP_204_NO_CONTENT)

    def test_view_isnt_available_to_not_owner(self):
        not_owner = self.create_test_user(email='not.owner@test.com')
        self.login_user_by_token(not_owner)

        response = self.client.delete(self.url)

        self.assert_response(response, status.HTTP_403_FORBIDDEN)

    def test_view_delete_advert_without_address(self):
        self.assertEqual(self.advert_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 0)

        response = self.client.delete(self.url)

        self.assert_response(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.advert_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

    def test_view_delete_advert_with_address(self):
        self.create_test_address(self.advert)

        self.assertEqual(self.advert_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 1)

        response = self.client.delete(self.url)

        self.assert_response(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.advert_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)
