from accounts.models import User
from django.utils.translation import gettext as _


class StaffProxy(User):
    class Meta:
        proxy = True
        verbose_name = _('staff')
        verbose_name_plural = _('staffs')


class CustomerProxy(User):
    class Meta:
        proxy = True
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
