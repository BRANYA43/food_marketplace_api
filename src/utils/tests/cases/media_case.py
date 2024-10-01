import io

from PIL import Image as PILImage
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from catalogs.models import Image, Advert
from utils.tests.cases import BaseTestCase
from django.test import override_settings
from tempfile import TemporaryDirectory

TEMP_MEDIA_ROOT = TemporaryDirectory(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT.name)
class MediaTestCase(BaseTestCase):
    TEMP_MEDIA_ROOT = TEMP_MEDIA_ROOT

    def tearDown(self):
        self.TEMP_MEDIA_ROOT.cleanup()

    @staticmethod
    def get_image_simple_uploaded_file(image_name: str) -> SimpleUploadedFile:
        image = PILImage.new('RGB', (100, 100), color=(255, 255, 255))
        image_io = io.BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        return SimpleUploadedFile(image_name, image_io.read(), 'image/png')

    @staticmethod
    def create_test_image(
        advert: Advert,
        file: SimpleUploadedFile = get_image_simple_uploaded_file('image_name.png'),
        **extra_fields,
    ) -> Image:
        return Image.objects.create(advert=advert, file=file, **extra_fields)
