from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse
from drf_standardized_errors import openapi_serializers
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny

from catalogs import models, serializers


@extend_schema(tags=['Category'])
@extend_schema_view(
    list=extend_schema(
        operation_id='category_list',
        summary=_('Retrieve category list.'),
        description=_('Retrieve category list.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_('Category list are retrieved successfully.'),
                response=serializers.CategoryListSerializer,
            ),
        },
    ),
    retrieve=extend_schema(
        operation_id='category_retrieve',
        summary=_('Retrieve detail of category.'),
        description=_('Retrieve detail of category.'),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_('Category is retrieved successfully.'),
                response=serializers.CategoryRetrieveSerializer,
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description=_("Category isn't found."),
                response=openapi_serializers.ErrorResponse404Serializer,
            ),
        },
    ),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Category.objects.filter(parent=None).order_by('name')
    serializer_classes = dict(
        list=serializers.CategoryListSerializer,
        retrieve=serializers.CategoryRetrieveSerializer,
    )
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        return self.serializer_classes[self.action]
