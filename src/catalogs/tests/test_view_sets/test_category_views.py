from django.urls import reverse
from rest_framework import status

from catalogs import serializers, models
from utils.tests import APITestCase


class CategoryRetrieveViewTest(APITestCase):
    def setUp(self) -> None:
        self.serializer_class = serializers.CategoryRetrieveSerializer
        self.model_class = models.Category
        self.category = self.model_class.objects.create(slug='plants', name='Plants')
        self.url = reverse('category-detail', args=[self.category.pk])

    def test_view_is_accessed_only_through_get_method(self):
        self.assert_not_allowed_methods(['post', 'put', 'patch', 'delete'], self.url)
        response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_allowed_for_unregister_user(self):
        response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_allowed_for_register_user(self):
        user = self.create_test_user()
        self.login_user_by_token(user)
        response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_returns_expected_data(self):
        expected_data = self.serializer_class(self.category).data

        response = self.client.get(self.url)

        self.assertEqual(response.data, expected_data)


class CategoryListViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('category-list')
        self.model_class = models.Category
        self.serializer_class = serializers.CategoryListSerializer

    def test_view_is_accessed_only_through_get_method(self):
        self.assert_not_allowed_methods(['post', 'put', 'patch', 'delete'], self.url)
        response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_allowed_for_unregister_user(self):
        response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_is_allowed_for_register_user(self):
        user = self.create_test_user()
        self.login_user_by_token(user)
        response = self.client.get(self.url)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_view_returns_expected_data(self):
        parent_category = self.model_class.objects.create(slug='plants', name='Plants')
        self.model_class.objects.create(slug='vegetables', name='Vegetables', parent=parent_category)

        qs = self.model_class.objects.filter(parent=None)
        expected_data = self.serializer_class(qs, many=True).data

        response = self.client.get(self.url)

        self.assertEqual(response.data['results'], expected_data)
