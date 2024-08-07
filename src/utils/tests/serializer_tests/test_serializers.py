from utils.serializers import AddressFieldSerializer
from utils.tests.cases import SerializerTestCase


class AddressFieldSerializerTest(SerializerTestCase):
    serializer_class = AddressFieldSerializer

    def setUp(self) -> None:
        self.user = self.create_test_user()
        self.address = self.create_test_address(self.user)

    def test_expected_fields_are_required(self):
        self.assert_required_fields(self.serializer_class, ['city', 'street', 'number'])

    def test_serializer_returns_expected_data(self):
        self.assert_output_serializer_data(
            self.serializer_class,
            instance=self.address,
            output_data=dict(
                city=self.address.city,
                street=self.address.street,
                number=self.address.number,
            ),
        )
