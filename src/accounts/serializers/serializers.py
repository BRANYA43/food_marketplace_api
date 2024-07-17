from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import mixins
from utils.serializers.mixins import AddressCreateUpdateMixin

User = get_user_model()


class UserDisableSerializer(serializers.ModelSerializer):
    token_class = RefreshToken

    class Meta:
        model = User
        fields = ('password',)

    def validate_password(self, password: str) -> str:
        if not self.instance.check_password(password):
            raise ValidationError(
                'Entered password is not user password.',
                'invalid_password',
            )
        return password

    def validate(self, attrs):
        if self.instance.is_superuser or self.instance.is_staff:
            raise ValidationError(
                'Disable staff user is impossible.',
                'disable_staff',
            )
        self.replace_user_data_to_fake_data()
        self.replace_user_address_data_to_fake_data()
        self.blacklist_tokens()
        return {}

    def replace_user_data_to_fake_data(self):
        self.instance.is_active = False
        self.instance.email = f'user.{self.instance.id}@disabled.com'
        self.instance.password = '-'
        self.instance.full_name = f'disabled user {self.instance.id}'
        self.instance.phone = '+38 (012) 345 6789'
        self.instance.save()

    def replace_user_address_data_to_fake_data(self):
        if (address := self.instance.address.first()) is not None:
            address.number = '-'
            address.save()

    def blacklist_tokens(self):
        tokens = OutstandingToken.objects.filter(user=self.instance)
        for token in tokens:
            self.token_class(token.token).blacklist()


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
