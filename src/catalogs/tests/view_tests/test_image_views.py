from rest_framework import status
from rest_framework.reverse import reverse

from catalogs.models import Image
from utils.tests.cases import MediaTestCase, ViewTestCase


class ImageMultipleDeleteViewTest(MediaTestCase, ViewTestCase):
    url = reverse('images-multiple-delete')

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)
        self.main_image = self.create_test_image(self.advert)
        self.extra_image = self.create_test_image(self.advert, type=Image.Type.EXTRA)

        self.data = dict(
            advert=self.advert.id,
            files=[str(self.extra_image.file)],
        )

        self.login_user_by_token(self.owner)

    def test_view_isnt_available_for_unauthenticated_user(self):
        self.logout_user_by_token(self.owner)
        response = self.client.post(self.url, self.data, format='json')
        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_isnt_available_for_authenticated_non_owner(self):
        non_owner = self.create_test_user('non_owner@test.com')
        self.login_user_by_token(non_owner)
        response = self.client.post(self.url, self.data, format='json')
        self.assert_response(response, status.HTTP_403_FORBIDDEN)

    def test_view_is_available_for_authenticated_owner(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assert_response(response, status.HTTP_204_NO_CONTENT)

    def test_view_deletes_image(self):
        self.assertEqual(Image.objects.count(), 2)

        response = self.client.post(self.url, self.data, format='json')
        self.assert_response(response, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Image.objects.count(), 1)

    def test_view_return_no_data(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assert_response(response, status.HTTP_204_NO_CONTENT, output_data=None)


class ImageMultipleCreateViewTest(MediaTestCase, ViewTestCase):
    url = reverse('images-multiple-create')

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)
        self.main_file = self.get_image_simple_uploaded_file('main_image.png')
        self.extra_file = self.get_image_simple_uploaded_file('extra_image.png')

        self.data = dict(
            advert=self.advert.id,
            files=[self.main_file, self.extra_file],
            types=[Image.Type.MAIN, Image.Type.EXTRA],
        )

        self.login_user_by_token(self.owner)

    def test_view_isnt_available_for_unauthenticated_user(self):
        self.logout_user_by_token(self.owner)
        response = self.client.post(self.url, self.data, format='multipart')
        self.assert_response(response, status.HTTP_401_UNAUTHORIZED)

    def test_view_is_available_for_authenticated_user(self):
        response = self.client.post(self.url, self.data, format='multipart')
        self.assert_response(response, status.HTTP_201_CREATED)

    def test_view_creates_images(self):
        self.assertEqual(Image.objects.count(), 0)

        response = self.client.post(self.url, self.data, format='multipart')
        self.assert_response(response, status.HTTP_201_CREATED)

        self.assertEqual(Image.objects.count(), 2)

        main_image = Image.objects.get(advert=self.advert, type=Image.Type.MAIN)
        extra_image = Image.objects.get(advert=self.advert, type=Image.Type.EXTRA)

        self.assertIn(self.main_file.name, main_image.file.name)
        self.assertIn(self.extra_file.name, extra_image.file.name)

    def test_view_returns_no_data(self):
        response = self.client.post(self.url, self.data, format='multipart')
        self.assert_response(response, status.HTTP_201_CREATED, output_data=None)
