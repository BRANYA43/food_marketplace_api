from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from drf_standardized_errors import openapi_serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings

from accounts import serializers

User = get_user_model()


@extend_schema(tags=['Accounts'])
@extend_schema_view(
    set_password_me=extend_schema(
        operation_id='user-set-password-me',
        summary='Set new password for a user.',
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description='User set a new password successfully.',
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid data.',
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='User is unauthenticated.',
                response=openapi_serializers.Error403Serializer,
            ),
        },
    ),
    update_me=extend_schema(
        operation_id='user-update-me',
        summary='Update user profile data.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='User profile data are update successfully.',
                response=serializers.UserUpdateSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid data.',
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='User is unauthenticated.',
                response=openapi_serializers.Error403Serializer,
            ),
        },
    ),
    disable_me=extend_schema(
        operation_id='user-disable-me',
        summary='Disable a user.',
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description='User is disabled successfully.'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid data.',
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='User is unauthenticated.',
                response=openapi_serializers.Error403Serializer,
            ),
        },
    ),
    register=extend_schema(
        operation_id='user-register',
        summary='Register a user.',
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                description='User is registered success.',
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid user credentials or user exists with this credentials.',
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
        },
    ),
    login=extend_schema(
        operation_id='user-login',
        summary='Log a user in.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='User is logged in successfully.',
                response=import_string(jwt_api_settings.TOKEN_OBTAIN_SERIALIZER),
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid credentials.',
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='User credentials are invalid.',
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
    logout=extend_schema(
        operation_id='user-logout',
        summary='Log a user out.',
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description='User is logged out successfully',
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid credentials.',
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='User is unauthenticated or token is invalid/expired/blacklisted.',
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
    refresh=extend_schema(
        operation_id='user-refresh',
        summary='Refresh access and refresh tokens.',
        description='Get a new access token and refresh the refresh token.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='Tokens is refresh successfully',
                response=import_string(jwt_api_settings.TOKEN_REFRESH_SERIALIZER),
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid data',
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='User is unauthenticated or token is invalid/expired/blacklisted.',
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
    verify=extend_schema(
        operation_id='user-verify',
        summary='Verify access or refresh tokens.',
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description='Token verifies successfully.',
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Token is blacklisted.',
                response=openapi_serializers.ValidationErrorResponseSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='Token is invalid/expired.',
                response=openapi_serializers.ErrorResponse401Serializer,
            ),
        },
    ),
)
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.filter(is_active=True)
    serializers_classes = dict(
        set_password_me=serializers.UserSetPasswordSerializer,
        update_me=serializers.UserUpdateSerializer,
        disable_me=serializers.UserDisableSerializer,
        register=serializers.UserRegisterSerializer,
        login=import_string(jwt_api_settings.TOKEN_OBTAIN_SERIALIZER),
        logout=import_string(jwt_api_settings.TOKEN_BLACKLIST_SERIALIZER),
        refresh=import_string(jwt_api_settings.TOKEN_REFRESH_SERIALIZER),
        verify=import_string(jwt_api_settings.TOKEN_VERIFY_SERIALIZER),
    )
    permission_classes = dict(
        set_password_me=(IsAuthenticated,),
        update_me=(IsAuthenticated,),
        disable_me=(IsAuthenticated,),
        register=(AllowAny,),
        login=(AllowAny,),
        logout=(IsAuthenticated,),
        refresh=(AllowAny,),
        verify=(AllowAny,),
    )

    def get_serializer_class(self):
        return self.serializers_classes[self.action]

    def get_current_user(self):
        return self.request.user

    def get_permissions(self):
        if self.action is None:
            return [AllowAny()]
        return [permission() for permission in self.permission_classes[self.action]]

    @action(methods=['put'], detail=False)
    def set_password_me(self, request):
        user = self.get_current_user()
        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['patch'], detail=False)
    def update_me(self, request):
        user = self.get_current_user()

        serializer = self.get_serializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def disable_me(self, request):
        user = self.get_current_user()
        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def login(self, request):
        return jwt_views.token_obtain_pair(request._request)

    @action(methods=['post'], detail=False)
    def logout(self, request):
        response = jwt_views.token_blacklist(request._request)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_204_NO_CONTENT
            response.data = None
        return response

    @action(methods=['post'], detail=False)
    def refresh(self, request):
        return jwt_views.token_refresh(request._request)

    @action(methods=['post'], detail=False)
    def verify(self, request):
        response = jwt_views.token_verify(request._request)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_204_NO_CONTENT
            response.data = None
        return response
