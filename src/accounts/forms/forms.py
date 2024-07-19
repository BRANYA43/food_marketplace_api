from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


User = get_user_model()


class BaseUserCreationForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), strip=False, widget=forms.PasswordInput())
    confirming_password = forms.CharField(label=_('Password Confirmation'), strip=False, widget=forms.PasswordInput())
    error_messages = dict(
        password_mismatch=_("The two password fields didn't match."),
    )

    class Meta:
        model = User
        fields = ('email',)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def clean_confirming_password(self):
        password = self.cleaned_data.get('password')
        confirming_password = self.cleaned_data.get('confirming_password')

        if password and confirming_password and password != confirming_password:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return confirming_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        return user


class StaffCreationForm(BaseUserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.is_staff = True
        if commit:
            user.save()
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        return user
