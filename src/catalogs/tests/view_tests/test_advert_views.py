from rest_framework import status
from rest_framework.reverse import reverse

from catalogs.serializers.serializers import AdvertListSerializer
from utils.tests.cases.view_test_case import ViewTestCase

LIST_URL = 'advert-list'


class AdvertListViewTest(ViewTestCase):
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
        serializer = self.create_serializer(self.serializer_class, instance=[self.advert], many=True)
        response = self.client.get(self.url)
        self.assert_response(
            response,
            status.HTTP_200_OK,
            output_data=serializer.data,
            used_paginate=True,
        )
