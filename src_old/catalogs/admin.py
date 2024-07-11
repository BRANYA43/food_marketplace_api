from django.contrib import admin

from catalogs import models


class AdvertAddressInline(admin.StackedInline):
    model = models.AdvertAddress
    fields = ('region', 'city', 'village', 'street', 'number')
    extra = 1


@admin.register(models.Advert)
class AdvertAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_displayed', 'updated_at', 'created_at')
    readonly_fields = ('updated_at', 'created_at')
    fieldsets = (
        (None, dict(fields=('is_displayed',))),
        ('Information', dict(fields=('category', 'title', 'price', 'descr'))),
        ('Delivery', dict(fields=('use_pickup', 'use_nova_post', 'use_courier'))),
        ('Dates', dict(fields=('updated_at', 'created_at'))),
    )
    search_fields = ('title', 'category__name')
    ordering = ('-created_at',)
    inlines = (AdvertAddressInline,)


class CategoryInline(admin.TabularInline):
    model = models.Category
    fields = ('name',)
    extra = 1
    show_change_link = True


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    fieldsets = (
        ('Info', dict(fields=('name',))),
        ('Dates', dict(fields=('updated_at', 'created_at'))),
    )
    readonly_fields = ('updated_at', 'created_at')
    inlines = (CategoryInline,)
    search_fields = ('name',)
    ordering = ('name',)
