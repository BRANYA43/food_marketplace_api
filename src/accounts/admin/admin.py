from typing import Any

from django.contrib import admin
from django.forms import Form

from utils.admin.inlines import AddressInline
from accounts.forms import StaffCreationForm, CustomerCreationForm
from accounts.models.proxy import StaffProxy, CustomerProxy


class BaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'phone', 'is_active', 'last_login', 'updated_at', 'joined_at')
    readonly_fields = ('last_login', 'updated_at', 'joined_at')
    ordering = ('-is_active',)
    search_fields = ('email', 'full_name', 'phone')
    list_filter = ('is_active',)

    queryset_filter_params: dict[str, Any] | None = None
    add_form: Form = None
    add_fieldsets: Any = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.queryset_filter_params:
            return qs.filter(**self.queryset_filter_params)
        return qs

    def get_fieldsets(self, request, obj=None):
        if not obj and self.add_fieldsets:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj and self.add_form:
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, change, **kwargs)


@admin.register(StaffProxy)
class StaffAdmin(BaseUserAdmin):
    fieldsets = (
        (None, dict(fields=('is_active',))),
        ('Personal info', dict(fields=('email', 'full_name', 'phone'))),
        ('Permissions', dict(fields=('is_staff', 'groups', 'user_permissions'))),
        ('Dates', dict(fields=('last_login', 'updated_at', 'joined_at'))),
    )
    filter_horizontal = ('groups', 'user_permissions')

    queryset_filter_params = dict(is_staff=True)
    add_form = StaffCreationForm
    add_fieldsets = (('Registration', dict(fields=('email', 'password', 'confirming_password'))),)
    extra_search_fields = ('groups',)

    def get_search_fields(self, request):
        self.search_fields += self.extra_search_fields
        print(self.search_fields)
        return self.search_fields


@admin.register(CustomerProxy)
class CustomerAdmin(BaseUserAdmin):
    fieldsets = (
        (None, dict(fields=('is_active',))),
        ('Personal info', dict(fields=('email', 'full_name', 'phone'))),
        ('Dates', dict(fields=('last_login', 'updated_at', 'joined_at'))),
    )
    inlines = (AddressInline,)

    queryset_filter_params = dict(is_staff=False)
    add_form = CustomerCreationForm
    add_fieldsets = (('Registration', dict(fields=('email', 'full_name', 'phone', 'password', 'confirming_password'))),)
