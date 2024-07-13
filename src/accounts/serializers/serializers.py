from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.serializers import mixins

User = get_user_model()


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
