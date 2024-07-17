from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.serializers import mixins
from utils.serializers.mixins import AddressCreateUpdateMixin

User = get_user_model()


class UserUpdateSerializer(mixins.PhoneNumberValidationMixin, AddressCreateUpdateMixin, serializers.ModelSerializer):
    """Serializer to update user data."""

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'address')


class UserRegisterSerializer(
    serializers.ModelSerializer, mixins.PasswordValidationMixin, mixins.PhoneNumberValidationMixin
):
    class Meta:
        model = User
        fields = ('email', 'password', 'full_name', 'phone')
        extra_kwargs = dict(
            password=dict(write_only=True),
            full_name=dict(required=True),
            phone=dict(required=True),
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
