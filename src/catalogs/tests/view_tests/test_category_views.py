from rest_framework import status
from rest_framework.reverse import reverse

from catalogs.models import Category
from catalogs.serializers import CategoryListSerializer
from catalogs.serializers.serializers import CategorySerializer
from utils.tests import ApiTestCase


class CategorySelectListViewTest(ApiTestCase):
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

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'get', status.HTTP_200_OK, {})
        self.assert_not_allowed_methods(self.url, ['post', 'put', 'patch', 'delete'])

    def test_view_is_accessed_for_unauthenticated_user(self):
        response = self.client.get(self.url)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_accessed_for_authenticated_user(self):
        self.login_user_by_token(self.user)
        response = self.client.get(self.url)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_returns_expected_data(self):
        expected_data = self.serializer_class(self.model.objects.filter(children=None), many=True).data

        response = self.client.get(self.url)

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertSequenceEqual(response.data['results'], expected_data)


class CategoryListViewTest(ApiTestCase):
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

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'get', status.HTTP_200_OK, {})
        self.assert_not_allowed_methods(self.url, ['post', 'put', 'patch', 'delete'])

    def test_view_is_accessed_for_unauthenticated_user(self):
        response = self.client.get(self.url)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_accessed_for_authenticated_user(self):
        self.login_user_by_token(self.user)
        response = self.client.get(self.url)

        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_returns_expected_data(self):
        expected_data = self.serializer_class(self.model.objects.filter(parent=None), many=True).data

        response = self.client.get(self.url)

        self.assert_response_status(response, status.HTTP_200_OK)
        self.assertSequenceEqual(response.data['results'], expected_data)
