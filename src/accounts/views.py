from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view
from drf_standardized_errors import openapi_serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied

from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts import serializers
from accounts.permissions import IsUnauthenticated, IsCurrentUser


@extend_schema(tags=['Accounts'])
@extend_schema_view(
    set_password_me=extend_schema(
        operation_id='user_set_password_me',
        summary=_('Set new password for current user.'),
        description=_('Set new password for current user.'),
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description=_('New password is set successfully.'),
                response=None,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description=_('Password or new password are invalid.'),
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('User is unauthenticated or token is invalid or expired.'),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
    disable_me=extend_schema(
        operation_id='user_disable_me',
        summary=_('Disable account of current user.'),
        description=_(
            'Disable account of current user and all associated tokens with this user will be added to black list.'
        ),
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description='User account was disabled successfully.',
                response=None,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('User is unauthenticated or token is invalid or expired.'),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description=_('User is already disabled or user is superuser and he try to disable his account.'),
                response=openapi_serializers.ErrorResponse403Serializer,
            ),
        },
    ),
    update_me=extend_schema(
        operation_id='user_update',
        summary=_('Update profile of current user.'),
        description=_('Update profile of current user.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_('User profile was updated successfully.'),
                response=serializers.UserProfileSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description=_('Invalid update data.'),
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('User is unauthenticated or token is invalid or expired.'),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
    retrieve_me=extend_schema(
        operation_id='user_me',
        summary=_('Retrieve profile of current user.'),
        description=_('Retrieve profile of current user.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_('User profile data are retrieved successfully.'),
                response=serializers.UserProfileSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('User is unauthenticated or token is invalid or expired.'),
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
                description=_('Invalid credentials or user exist with credentials.'),
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
                response=import_string(jwt_api_settings.TOKEN_OBTAIN_SERIALIZER),
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
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description=_('User logged out successfully.'),
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description=_('Invalid data.'),
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('User is unauthenticated or token is invalid, expired or blacklisted.'),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
    refresh=extend_schema(
        operation_id='user_refresh_token',
        summary=_('Refresh token.'),
        description=_('Refresh a lifetime and expiry of user refresh token and return new user access token.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_('Token was refreshed successfully.'),
                response=jwt_api_settings.TOKEN_REFRESH_SERIALIZER,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description=_('Invalid data.'),
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description=_('Refresh token is invalid, expired or blacklisted.'),
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
)
class UserViewSet(viewsets.ViewSet):
    serializer_classes = {
        'set_password_me': serializers.UserPasswordSetSerializer,
        'update_me': serializers.UserProfileSerializer,
        'retrieve_me': serializers.UserProfileSerializer,
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

    @action(methods=['put'], detail=False, permission_classes=[IsCurrentUser])
    def set_password_me(self, request):
        serializer = self.get_serializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], permission_classes=[IsCurrentUser])
    def disable_me(self, request):
        if request.user.is_superuser:
            raise PermissionDenied(detail='Superuser cannot be disabled.')
        user = request.user
        user.is_active = False
        user.save()

        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            RefreshToken(token.token).blacklist()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsCurrentUser])
    def update_me(self, request):
        serializer = self.get_serializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsCurrentUser])
    def retrieve_me(self, request):
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
        response = jwt_views.token_blacklist(request._request)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_204_NO_CONTENT
            response.data = None
        return response

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        return jwt_views.token_refresh(request._request)
