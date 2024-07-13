from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from utils.tests import ApiTestCase

User = get_user_model()


class UserRegisterViewTest(ApiTestCase):
    url = reverse('user-register')
    model = User

    def setUp(self) -> None:
        self.data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            full_name=self.TEST_FULL_NAME,
            phone=self.TEST_PHONE,
        )

    def test_view_allows_only_post_method(self):
        self.assert_allowed_method(self.url, 'post', status.HTTP_201_CREATED, self.data)
        self.assert_not_allowed_methods(self.url, ['get', 'put', 'patch', 'delete'])

    def test_view_is_accessed_for_unregister_user(self):
        response = self.client.post(self.url, self.data)
        self.assert_response_status(response, status.HTTP_201_CREATED)

    def test_view_creates_user(self):
        self.assertEqual(self.model.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.count(), 1)

        user = self.model.objects.first()

        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertEqual(user.full_name, self.data['full_name'])
        self.assertEqual(user.phone, self.data['phone'])

    def test_view_doesnt_create_existed_user(self):
        self.create_test_user(**self.data)

        self.assertEqual(self.model.objects.count(), 1)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.model.objects.count(), 1)

    def test_view_doesnt_create_user_by_invalid_credentials(self):
        self.data['email'] = 'invalid_email'

        self.assertEqual(self.model.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.model.objects.count(), 0)
        self.assertIn('email', response.data['errors'][0]['attr'])

    def test_view_doesnt_return_data(self):
        response = self.client.post(self.url, self.data)
        self.assertIsNone(response.data)
