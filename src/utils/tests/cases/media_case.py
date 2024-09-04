import io

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

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
        image = Image.new('RGB', (100, 100), color=(255, 255, 255))
        image_io = io.BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        return SimpleUploadedFile(image_name, image_io.read(), 'image/png')
