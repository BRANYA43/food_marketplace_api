from django.contrib import admin
from orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'customer', 'status', 'created_at', 'is_paid']
    list_filter = ['status', 'is_paid']
    search_fields = ['uuid', 'customer__username']
