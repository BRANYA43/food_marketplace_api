from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts import validators, services

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'phone']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'full_name': {'required': True, 'min_length': 3},
            'phone': {'required': True},
        }

    def validate_phone(self, phone):
        validators.validate_ukrainian_phone(phone)
        phone = services.normalize_phone_to_ukrainian_format(phone)
        return phone

    def create(self, validated_data: dict):
        return User.objects.create_user(**validated_data)
