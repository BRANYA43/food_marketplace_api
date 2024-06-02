from django.utils.translation import gettext as _
from rest_framework.permissions import BasePermission


class IsUnauthenticated(BasePermission):
    message = _('User is already authenticated.')

    def has_permission(self, request, view):
        user = request.user
        return not user.is_authenticated
