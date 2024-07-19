from django.contrib import admin
from django.utils.translation import gettext as _

from catalogs.admin.inlines import SubCategoryInline
from catalogs.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_parent', 'is_child', 'updated_at', 'created_at')
    fieldsets = (
        ('Info', dict(fields=('name', 'is_parent', 'is_child'))),
        ('Dates', dict(fields=('updated_at', 'created_at'))),
    )
    readonly_fields = ('is_parent', 'is_child', 'updated_at', 'created_at')
    ordering = ('parent__name', 'name')
    search_fields = ('parent__name', 'name')
    inlines = (SubCategoryInline,)

    @admin.display(boolean=True, ordering=('is_parent',), description=_('Is Parent'))
    def is_parent(self, instance: Category):
        return instance.is_parent

    @admin.display(boolean=True, ordering=('is_child',), description=_('Is Child'))
    def is_child(self, instance: Category):
        return instance.is_child
