from django.contrib.contenttypes.admin import GenericStackedInline

from utils.models import Address


class AddressInline(GenericStackedInline):
    model = Address
    extra = 1
    max_num = 1
