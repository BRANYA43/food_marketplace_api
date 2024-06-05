from django.utils.translation import gettext as _
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsCurrentUser(IsAuthenticated):
    message = _("Current user isn't owner this account.")

    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk


class IsUnauthenticated(BasePermission):
    message = _('User is already authenticated.')

    def has_permission(self, request, view):
        user = request.user
        return not user.is_authenticated
