from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        extra_fields['is_active'] = True
        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError('Email cannot be empty.')

        if not password:
            raise ValueError('Password cannot be empty.')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        return user
