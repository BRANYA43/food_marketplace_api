from django.db.models import Manager
from rest_framework import serializers

from utils import models


class AddressFieldSerializer(serializers.ModelSerializer):
    """Serializer to use in the other serializers as address field."""

    class Meta:
        model = models.Address
        fields = ('region', 'city', 'village', 'street', 'number')

    def get_attribute(self, instance):
        if isinstance(instance, Manager):
            return instance.first()
        return super().get_attribute(instance)

    def to_representation(self, instance):
        if isinstance(instance, Manager):
            instance = instance.first()
        return super().to_representation(instance)
