import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import QuerySet
from django.test import TransactionTestCase, override_settings

from catalogs import models

temp_media = settings.BASE_DIR / 'temp_media/'


@override_settings(MEDIA_ROOT=temp_media)
class ReorderImageOrderSignalTest(TransactionTestCase):
    def setUp(self) -> None:
        self.model_class = models.AdvertImage
        self.user = get_user_model().objects.create_user(email='test@test.com', password='qwe123!@#')
        self.category = models.Category.objects.create(name='vegetables')
        self.advert = models.Advert.objects.create(
            user=self.user,
            category=self.category,
            title='Potato',
            price='100.00',
        )
        self.data = dict(
            advert=self.advert,
            origin=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
        )

        self.model_class.objects.bulk_create(
            [self.model_class(**self.data, order_num=i) for i in range(5)],
        )

        self.images = self.model_class.objects.all().order_by('order_num')

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(temp_media)

    def assert_image_order(self, images: QuerySet):
        for i, image in enumerate(images):
            self.assertEqual(image.order_num, i)

    def test_signal_reorders_image_order_correctly_for_deleted_first_image(self):
        self.images.first().delete()
        self.assert_image_order(self.images)

    def test_signal_reorders_image_order_correctly_for_deleted_last_image(self):
        self.images.last().delete()
        self.assert_image_order(self.images)

    def test_signal_reorders_image_order_correctly_for_deleted_middle_image(self):
        self.images.filter(order_num=3).delete()
        self.assert_image_order(self.images)

    def test_signal_reorders_image_order_correctly_for_several_deleted_images_from_start(self):
        self.images.filter(order_num__in=[0, 1]).delete()
        self.assert_image_order(self.images)

    def test_signal_reorders_image_order_correctly_for_several_deleted_images_from_end(self):
        self.images.filter(order_num__in=[3, 4]).delete()
        self.assert_image_order(self.images)

    def test_signal_reorders_image_order_correctly_for_several_deleted_images_from_middle(self):
        self.images.filter(order_num__in=[2, 3]).delete()
        self.assert_image_order(self.images)


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
        )
        self.data = dict(
            advert=self.advert,
            origin=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(temp_media, ignore_errors=True)

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

    def test_signal_do_nothing_if_order_num_isnt_none(self):
        expected_value = 1
        img = models.AdvertImage.objects.create(**self.data, order_num=expected_value)
        self.assertEqual(img.order_num, expected_value)
