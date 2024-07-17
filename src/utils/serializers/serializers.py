from django.db.models import Manager
from rest_framework import serializers

from utils import models


class AddressFieldSerializer(serializers.ModelSerializer):
    """Serializer to use in the other serializers as address field."""

    class Meta:
        model = models.Address
        fields = ('city', 'street', 'number')

    def get_attribute(self, instance):
        if isinstance(instance, Manager):
            return instance.first()
        return super().get_attribute(instance)

    def to_representation(self, instance):
        if isinstance(instance, Manager):
            if (instance := instance.first()) is None:
                return {}
        return super().to_representation(instance)
