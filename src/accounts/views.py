from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, status

from rest_framework_simplejwt import views as jwt_views

from accounts import serializers
from accounts.permissions import IsUnauthenticated


class UserViewSet(viewsets.ViewSet):
    def get_serializer_class(self):
        """
        Return a serializer class by the action.
        """
        match self.action:
            case 'register':
                return serializers.UserRegisterSerializer
            case 'login':
                return import_string(settings.SIMPLE_JWT['TOKEN_OBTAIN_SERIALIZER'])
            case 'logout':
                return import_string(settings.SIMPLE_JWT['TOKEN_BLACKLIST_SERIALIZER'])
            case 'refresh':
                return import_string(settings.SIMPLE_JWT['TOKEN_REFRESH_SERIALIZER'])

    def get_serializer(self, *args, **kwargs):
        serializer = self.get_serializer_class()
        return serializer(*args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[IsUnauthenticated])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(data={'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsUnauthenticated])
    def login(self, request):
        return jwt_views.token_obtain_pair(request._request)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        return jwt_views.token_blacklist(request._request)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        return jwt_views.token_refresh(request._request)
