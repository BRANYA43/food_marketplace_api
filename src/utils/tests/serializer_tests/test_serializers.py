from utils.serializers import AddressFieldSerializer
from utils.tests.cases import BaseTestCase


class AddressFieldSerializerTest(BaseTestCase):
    serializer_class = AddressFieldSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.address = self.create_test_address(self.user)

    def test_serializer_returns_expected_data(self):
        self.assert_serializer_output_data(
            self.serializer_class,
            instance=self.address,
            expected_data=dict(
                city=self.address.city,
                street=self.address.street,
                number=self.address.number,
            ),
        )
