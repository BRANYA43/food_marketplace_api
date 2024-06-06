from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view
from drf_standardized_errors import openapi_serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, status

from rest_framework_simplejwt import views as jwt_views

from accounts import serializers
from accounts.permissions import IsUnauthenticated, IsCurrentUser


@extend_schema(tags=['Accounts'])
@extend_schema_view(
    update_me=extend_schema(
        operation_id='user_update',
        summary=_('Update profile of current user.'),
        description=_('Update profile of current user.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_('User profile was updated successfully.'),
                response=serializers.UserProfileUpdateSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description=_('Invalid data.'),
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('User not auth.'),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
    me=extend_schema(
        operation_id='user_me',
        summary=_('Get profile of current user.'),
        description=_('Get profile of current user.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_('User profile data.'),
                response=serializers.UserProfileSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('User not auth.'),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
    register=extend_schema(
        operation_id='user_register',
        summary=_('Register user.'),
        description=_('Register user by email, password, phone and full_name.'),
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                description=_('User registered successfully.'),
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description=_('Invalid credentials.'),
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
        },
    ),
    login=extend_schema(
        operation_id='user_login',
        summary=_('Log a user in.'),
        description=_('Log a user in by creating new refresh and access user tokens.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='User logged in successfully.',
                response=import_string(settings.SIMPLE_JWT['TOKEN_OBTAIN_SERIALIZER']),
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description=_('Invalid credentials.'),
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_("Account isn't activate."),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description=_('User already authenticated.'),
                response=openapi_serializers.ErrorResponse403Serializer,
            ),
        },
    ),
    logout=extend_schema(
        operation_id='user_logout',
        summary=_('Log a user out.'),
        description=_('Log a user out by adding all user tokens to the blacklist.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_('User logged out successfully.'),
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('Credentials were not provided; Token is invalid, expired or blacklisted;'),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
    refresh=extend_schema(
        operation_id='user_refresh_token',
        summary=_('Refresh token.'),
        description=_('Refresh a expiry of user refresh token and return new user access token.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_('Token was refreshed successfully.'),
                response=import_string(settings.SIMPLE_JWT['TOKEN_REFRESH_SERIALIZER']),
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('Token is invalid, expired or blacklisted;'),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
)
class UserViewSet(viewsets.ViewSet):
    serializer_classes = {
        'update_me': serializers.UserProfileUpdateSerializer,
        'me': serializers.UserProfileSerializer,
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

    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsCurrentUser])
    def update_me(self, request):
        serializer = self.get_serializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsCurrentUser])
    def me(self, request):
        serializer = self.get_serializer(instance=request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsUnauthenticated])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[IsUnauthenticated])
    def login(self, request):
        return jwt_views.token_obtain_pair(request._request)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        return jwt_views.token_blacklist(request._request)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        return jwt_views.token_refresh(request._request)
