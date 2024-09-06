from django.contrib import admin
from django.utils.translation import gettext as _

from catalogs.models import Category
from catalogs.models.proxies import MainImage, ExtraImage


class ExtraImageInline(admin.StackedInline):
    model = ExtraImage
    extra = 0
    fields = ('file',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(type=ExtraImage.Type.EXTRA)


class MainImageInline(admin.StackedInline):
    model = MainImage
    extra = 1
    fields = ('file',)
    max_num = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(type=MainImage.Type.MAIN)


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
