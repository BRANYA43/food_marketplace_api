from rest_framework import serializers

from utils import models


class AddressFieldSerializer(serializers.ModelSerializer):
    """Serializer to use in the other serializers as address field."""

    class Meta:
        model = models.Address
        fields = ('region', 'city', 'village', 'street', 'number')
