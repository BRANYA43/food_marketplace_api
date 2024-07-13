from django.contrib.auth.password_validation import validate_password


class PasswordValidationMixin:
    """Serializer Mixin to validate a password"""

    def validate_password(self, value: str):
        validate_password(value, self.instance)  # type: ignore
        return value
