from utils import serializers
from utils.tests import ApiTestCase


class AddressFieldSerializerTest(ApiTestCase):
    serializer_class = serializers.AddressFieldSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.address = self.create_test_address(self.user)

    def test_serializer_returns_expected_data(self):
        expected_data = dict(
            region=self.address.region,
            city=self.address.city,
            village=self.address.village,
            street=self.address.street,
            number=self.address.number,
        )

        serializer = self.serializer_class(self.address)
        self.assertDictEqual(serializer.data, expected_data)
