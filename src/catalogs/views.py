from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from catalogs.models import Category
from catalogs.serializers import CategoryListSerializer


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
)
class CategoryViewSet(viewsets.GenericViewSet):
    model = Category
    serializer_classes = dict(
        list=CategoryListSerializer,
    )
    permission_classes = (AllowAny,)
    queryset = Category.objects.filter(parent=None)

    def get_serializer_class(self):
        return self.serializer_classes[self.action]

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        if serializer.data:
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
