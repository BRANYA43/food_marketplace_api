from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from drf_standardized_errors import openapi_serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings

from accounts import serializers

User = get_user_model()


@extend_schema(tags=['Accounts'])
@extend_schema_view(
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
                response=jwt_api_settings.TOKEN_OBTAIN_SERIALIZER,
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
)
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.filter(is_active=True)
    serializers_classes = dict(
        register=serializers.UserRegisterSerializer,
        login=jwt_api_settings.TOKEN_OBTAIN_SERIALIZER,
    )
    permission_classes = dict(
        register=(AllowAny,),
        login=(AllowAny,),
    )

    def get_serializer_class(self):
        return self.serializers_classes[self.action]

    def get_permissions(self):
        if self.action is None:
            return [AllowAny()]
        return [permission() for permission in self.permission_classes[self.action]]

    @action(methods=['post'], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def login(self, request):
        return jwt_views.token_obtain_pair(request._request)
