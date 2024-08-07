from catalogs.models.models import Advert
from utils.models import Address
from utils.tests.cases import BaseTestCase


class DeleteAdvertAddressSignalTest(BaseTestCase):
    advert_model = Advert
    address_model = Address

    def setUp(self):
        self.owner = self.create_test_user()
        self.category = self.create_test_category()
        self.advert = self.create_test_advert(self.owner, self.category)
        self.address = self.create_test_address(self.advert)

    def test_signal_delete_advert_address(self):
        self.assertEqual(self.advert_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 1)

        self.advert.delete()

        self.assertEqual(self.advert_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)

    def test_signal_doesnt_raise_error_if_advert_address_is_none(self):
        self.address.delete()

        self.assertEqual(self.advert_model.objects.count(), 1)
        self.assertEqual(self.address_model.objects.count(), 0)

        self.advert.delete()

        self.assertEqual(self.advert_model.objects.count(), 0)
        self.assertEqual(self.address_model.objects.count(), 0)
