from catalogs.models.proxies import MainImage, ExtraImage
from utils.tests.cases import MediaTestCase


class ExtraImageProxyModelTest(MediaTestCase):
    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(owner=self.owner, category=self.category)
        self.file = self.get_image_simple_uploaded_file('extra_image.png')

    def test_proxy_model_save_image_type_as_main(self):
        img = ExtraImage.objects.create(advert=self.advert, file=self.file)
        self.assertEqual(img.type, img.type.EXTRA)


class MainImageProxyModelTest(MediaTestCase):
    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(owner=self.owner, category=self.category)
        self.file = self.get_image_simple_uploaded_file('main_image.png')

    def test_proxy_model_save_image_type_as_main(self):
        img = MainImage.objects.create(advert=self.advert, file=self.file)
        self.assertEqual(img.type, img.type.MAIN)
