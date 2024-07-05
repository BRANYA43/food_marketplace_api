from django.contrib import admin

from catalogs import models


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
