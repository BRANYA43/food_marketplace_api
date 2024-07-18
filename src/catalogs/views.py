from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from catalogs.models import Category
from catalogs.serializers import CategoryListSerializer
from catalogs.serializers.serializers import CategorySerializer


@extend_schema(tags=['Catalog'])
@extend_schema_view(
    list=extend_schema(
        operation_id='category-list',
        summary='Get category list',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='Category list is got successfully.',
            ),
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description='Category list is empty.',
            ),
        },
    ),
    select_list=extend_schema(
        operation_id='category-select-list',
        summary='Get category list, that have no sub category.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='Category list is got successfully.',
            ),
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description='Category list is empty.',
            ),
        },
    ),
)
class CategoryViewSet(viewsets.GenericViewSet):
    model = Category
    serializer_classes = dict(
        list=CategoryListSerializer,
        select_list=CategorySerializer,
    )
    permission_classes = (AllowAny,)
    queryset = model.objects.filter(parent=None)

    def get_serializer_class(self):
        return self.serializer_classes[self.action]

    def get_queryset(self):
        querysets = dict(
            select_list=self.model.objects.filter(children=None),
        )
        return querysets[self.action] if self.action in querysets else super().get_queryset()

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        if serializer.data:
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def select_list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        if serializer.data:
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
