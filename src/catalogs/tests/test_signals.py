import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TransactionTestCase, override_settings

from catalogs import models

temp_media = settings.BASE_DIR / 'temp_media/'


@override_settings(MEDIA_ROOT=temp_media)
class SetImageOrderSignalTest(TransactionTestCase):
    def setUp(self) -> None:
        self.model_class = models.AdvertImage
        self.user = get_user_model().objects.create_user(email='test@test.com', password='qwe123!@#')
        self.category = models.Category.objects.create(name='vegetables')
        self.advert = models.Advert.objects.create(
            user=self.user,
            category=self.category,
            title='Potato',
            price='100.00',
            address='potato street',
        )
        self.data = dict(
            advert=self.advert,
            origin=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(temp_media)

    def test_signal_sets_order_num_as_0_for_first_image(self):
        img = models.AdvertImage.objects.create(**self.data)

        self.assertEqual(img.order_num, 0)

    def test_signal_increment_order_num_on_1_for_next_image(self):
        img0 = models.AdvertImage.objects.create(**self.data)
        img1 = models.AdvertImage.objects.create(**self.data)

        self.assertEqual(img0.order_num, 0)
        self.assertEqual(img1.order_num, 1)

    def test_signal_sets_order_for_only_create_operation(self):
        img = models.AdvertImage.objects.create(**self.data)

        self.assertEqual(img.order_num, 0)
        new_origin = SimpleUploadedFile(name='test_image1.jpg', content=b'', content_type='image/jpeg')

        img.origin = new_origin
        img.save()
