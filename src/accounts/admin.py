from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'type', 'is_active', 'is_staff', 'is_superuser', 'joined_at')
    fieldsets = (
        ('Info', {'fields': ('email', 'type', 'full_name', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'updated_at', 'joined_at')}),
    )
    readonly_fields = ('last_login', 'updated_at', 'joined_at')
    filter_horizontal = ('groups', 'user_permissions')

    def get_fieldsets(self, request, obj=None):
        if obj:
            return super().get_fieldsets(request, obj)
        return (('Register', {'fields': ('email', 'password')}),)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)