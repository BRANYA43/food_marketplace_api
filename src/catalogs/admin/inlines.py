from django.contrib import admin
from django.utils.translation import gettext as _

from catalogs.models import Category, Image


class MainImageInline(admin.StackedInline):
    model = Image
    extra = 1
    fields = ('file',)


class SubCategoryInline(admin.TabularInline):
    model = Category
    extra = 1
    show_change_link = True
    fields = ('name', 'is_parent', 'is_child')
    readonly_fields = ('is_parent', 'is_child')
    verbose_name = _('sub category')
    verbose_name_plural = _('sub categories')

    @admin.display(boolean=True, ordering=('is_parent',), description=_('Is Parent'))
    def is_parent(self, instance: Category):
        return instance.is_parent

    @admin.display(boolean=True, ordering=('is_child',), description=_('Is Child'))
    def is_child(self, instance: Category):
        return instance.is_child
