from copy import deepcopy

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts import validators, services, models

User = get_user_model()


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserAddress
        fields = ('user', 'region', 'city', 'village', 'street', 'number')
        extra_kwargs = dict(user=dict(required=False, write_only=True))

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.full_clean()
        instance.save()
        return instance

    def create(self, validated_data):
        instance = models.UserAddress(**validated_data)
        instance.full_clean()
        instance.save()
        return instance


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


class UserProfileSerializer(BaseUserSerializer):
    address = UserAddressSerializer(required=False)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'address')

    def update(self, instance, validated_data: dict):
        if 'address' in validated_data:
            address_data = validated_data.pop('address')
            self._update_address(instance, address_data)
            instance.refresh_from_db(fields=['address'])

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.full_clean()
        instance.save()

        return instance

    def _update_address(self, user, data):
        if data is not None:
            if (address := getattr(user, 'address', None)) is not None:
                serializer = UserAddressSerializer(address, data, partial=True)
            else:
                data['user'] = user.pk
                serializer = UserAddressSerializer(data=data)

            serializer.is_valid(raise_exception=True)
            serializer.save()


class UserRegisterSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['email', 'password', 'full_name', 'phone']
        extra_kwargs = deepcopy(BaseUserSerializer.Meta.extra_kwargs)
        extra_kwargs['full_name']['required'] = True
        extra_kwargs['phone'] = {'required': True}

    def create(self, validated_data: dict):
        return User.objects.create_user(**validated_data)


class UserPasswordSetSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('password', 'new_password')
        extra_kwargs = {
            'password': {'min_length': 8, 'write_only': True},
        }

    def validate_password(self, password):
        if not self.instance.check_password(password):
            raise ValidationError(
                _("Entered password isn't user password."),
                'invalid_password',
            )
        return password

    def validate_new_password(self, password):
        validate_password(password, self.instance)
        return password

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.full_clean()
        instance.save()
        return instance
