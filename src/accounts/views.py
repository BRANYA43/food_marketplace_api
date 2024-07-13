from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from drf_standardized_errors import openapi_serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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
)
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.filter(is_active=True)
    serializers_classes = dict(
        register=serializers.UserRegisterSerializer,
    )
    permission_classes = dict(
        register=(AllowAny,),
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
