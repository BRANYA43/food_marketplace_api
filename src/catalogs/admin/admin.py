from django.contrib import admin
from django.utils.translation import gettext as _

from catalogs.admin.inlines import SubCategoryInline, MainImageInline, ExtraImageInline
from catalogs.models import Category, Advert
from utils.admin.inlines import AddressInline


@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'price', 'quantity', 'updated_at', 'created_at')
    fieldsets = (
        ('Info', dict(fields=('owner', 'name', 'category', 'price', 'quantity', 'descr'))),
        ('Delivery', dict(fields=('pickup', 'nova_post', 'courier'))),
        ('Dates', dict(fields=('updated_at', 'created_at'))),
    )
    readonly_fields = ('updated_at', 'created_at')
    ordering = ('-created_at',)
    search_fields = ('name', 'owner__full_name', 'category__name')
    inlines = (AddressInline, MainImageInline, ExtraImageInline)


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
