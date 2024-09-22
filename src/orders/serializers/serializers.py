from rest_framework import serializers
from orders.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'uuid', 'customer', 'shipping_address', 'payment_method',
            'shipping_method', 'status', 'is_paid', 'notes'
        ]

    def create(self, validated_data):
        return super().create(validated_data)
