from copy import deepcopy

from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts import validators, services

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields: list[str] | str = '__all__'
        extra_kwargs = {
            'password': {'min_length': 8, 'write_only': True},
            'full_name': {'min_length': 3},
        }

    def validate_phone(self, phone):
        validators.validate_ukrainian_phone(phone)
        phone = services.normalize_phone_to_ukrainian_format(phone)
        return phone


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['email', 'full_name', 'phone']
        read_only_fields = fields


class UserRegisterSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['email', 'password', 'full_name', 'phone']
        extra_kwargs = deepcopy(BaseUserSerializer.Meta.extra_kwargs)
        extra_kwargs['full_name']['required'] = True
        extra_kwargs['phone'] = {'required': True}

    def create(self, validated_data: dict):
        return User.objects.create_user(**validated_data)
