from django.conf import settings
from django.utils.module_loading import import_string
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, status

from rest_framework_simplejwt import views as jwt_views

from accounts import serializers
from accounts.permissions import IsUnauthenticated


class UserViewSet(viewsets.ViewSet):
    serializer_classes = {
        'register': serializers.UserRegisterSerializer,
        'login': import_string(settings.SIMPLE_JWT['TOKEN_OBTAIN_SERIALIZER']),
        'logout': import_string(settings.SIMPLE_JWT['TOKEN_BLACKLIST_SERIALIZER']),
        'refresh': import_string(settings.SIMPLE_JWT['TOKEN_REFRESH_SERIALIZER']),
    }

    def get_serializer_class(self):
        """
        Return a serializer class by the action.
        """
        return self.serializer_classes[self.action]

    def get_serializer(self, *args, **kwargs):
        serializer = self.get_serializer_class()
        return serializer(*args, **kwargs)

    @extend_schema(
        operation_id='user_register',
        description='Register user by email and password.',
        responses={
            201: OpenApiResponse(
                description='User was registered successfully.',
            ),
        },
    )
    @action(detail=False, methods=['post'], permission_classes=[IsUnauthenticated])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id='user_login',
        description='Log a user in by creating new refresh and access user tokens.',
        responses={
            200: OpenApiResponse(description='User logged in successfully.', response=serializer_classes['login']),
        },
    )
    @action(detail=False, methods=['post'], permission_classes=[IsUnauthenticated])
    def login(self, request):
        return jwt_views.token_obtain_pair(request._request)

    @extend_schema(
        operation_id='user_logout',
        description='Log a user out by adding all user tokens to the blacklist.',
        responses={
            200: OpenApiResponse(description='User logged out successfully.'),
        },
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        return jwt_views.token_blacklist(request._request)

    @extend_schema(
        operation_id='user_refresh_token',
        description='Refresh a expiry of user refresh token and return new user access token.',
        responses={
            200: OpenApiResponse(
                description='Token was refreshed successfully.', response=serializer_classes['refresh']
            ),
        },
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        return jwt_views.token_refresh(request._request)
