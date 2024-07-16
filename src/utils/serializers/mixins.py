from utils import models
from utils.serializers.serializers import AddressFieldSerializer


class AddressMixin:
    """Serializer mixin to update or create address for models that have only one address."""

    address = AddressFieldSerializer(required=False)

    def get_fields(self):
        fields = super().get_fields()
        fields['address'] = AddressFieldSerializer(required=False)
        return fields

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)

        instance = super().create(validated_data)

        if address_data:
            self._update_or_create_address(instance, address_data)
            instance.refresh_from_db()

        return instance

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)

        instance = super().update(instance, validated_data)

        if address_data:
            self._update_or_create_address(instance, address_data)
            instance.refresh_from_db()

        return instance

    def _update_or_create_address(self, content_obj, data: dict):
        if (address := content_obj.address.first()) is not None:
            for field, value in data.items():
                setattr(address, field, value)
        else:
            address = models.Address(**data, content_obj=content_obj)

        address.full_clean()
        address.save()
