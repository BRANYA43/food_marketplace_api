from typing import Any

from django.contrib import admin
from django.forms import Form


class BaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'phone', 'is_active', 'last_login', 'updated_at', 'joined_at')
    readonly_fields = ('last_login', 'updated_at', 'joined_at')
    ordering = ('-is_active',)
    search_fields = ('email', 'full_name', 'phone')
    list_filter = ('is_active',)

    queryset_filter_params: dict[str, Any] | None = None
    add_form: Form = None
    add_fieldsets = None

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
