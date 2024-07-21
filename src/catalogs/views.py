from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiParameter
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
                response=CategoryListSerializer,
            ),
        },
    ),
    select_list=extend_schema(
        operation_id='category-select-list',
        summary='Get category list, that have no sub category.',
        parameters=[
            OpenApiParameter('limit', int, 'query', description='Number of results to return per page.'),
            OpenApiParameter('offset', int, 'query', description='The initial index from which to return the results.'),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='Category list is got successfully.',
                response=CategorySerializer,
                examples=[
                    OpenApiExample(
                        'Example',
                        value=dict(
                            count=123,
                            next='http://api.example.org/accounts/?offset=400&limit=100',
                            previous='http://api.example.org/accounts/?offset=200&limit=100',
                            results=[
                                dict(
                                    id=0,
                                    name='string',
                                ),
                            ],
                        ),
                    ),
                ],
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

    def _list(self, request):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        return self._list(request)

    @action(methods=['get'], detail=False)
    def select_list(self, request):
        return self._list(request)
