from rest_framework import status
from rest_framework.reverse import reverse

from catalogs.models import Category
from catalogs.serializers import CategoryListSerializer
from catalogs.serializers.serializers import CategorySerializer
from utils.tests.cases import ViewTestCase


class CategorySelectListViewTest(ViewTestCase):
    url = reverse('category-select-list')
    serializer_class = CategorySerializer
    model = Category

    def setUp(self) -> None:
        self.user = self.create_test_user()
        food = self.create_test_category(name='Food')
        vegetables = self.create_test_category(name='Vegetables', parent=food)
        self.create_test_category(name='Tomato', parent=vegetables)
        self.create_test_category(name='Fruits', parent=food)
        self.create_test_category('All For Home')

    def test_view_allows_only_get_method(self):
        self.assert_http_methods_availability(
            self.url, ['post', 'put', 'patch', 'delete'], status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assert_http_methods_availability(self.url, ['get'], status.HTTP_200_OK)

    def test_view_is_available_to_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assert_response(response, status.HTTP_200_OK)

    def test_view_returns_data(self):
        response = self.client.get(self.url)
        self.assert_response(
            response,
            status.HTTP_200_OK,
            output_data=self.create_serializer_deprecated(
                self.serializer_class,
                instance=self.model.objects.filter(children=None),
                many=True,
            ).data,
            used_paginate=True,
        )


class CategoryListViewTest(ViewTestCase):
    url = reverse('category-list')
    serializer_class = CategoryListSerializer
    model = Category

    def setUp(self) -> None:
        self.user = self.create_test_user()
        food = self.create_test_category(name='Food')
        vegetables = self.create_test_category(name='Vegetables', parent=food)
        self.create_test_category(name='Tomato', parent=vegetables)
        self.create_test_category(name='Fruits', parent=food)
        self.create_test_category('All For Home')

    def test_view_allows_only_get_method(self):
        self.assert_http_methods_availability(
            self.url, ['post', 'put', 'patch', 'delete'], status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assert_http_methods_availability(self.url, ['get'], status.HTTP_200_OK)

    def test_view_is_available_to_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assert_response(response, status.HTTP_200_OK)

    def test_view_returns_data(self):
        response = self.client.get(self.url)
        self.assert_response(
            response,
            status.HTTP_200_OK,
            output_data=self.create_serializer_deprecated(
                self.serializer_class,
                instance=self.model.objects.filter(parent=None),
                many=True,
            ).data,
            used_paginate=True,
        )
