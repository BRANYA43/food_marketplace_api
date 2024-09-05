from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from catalogs.models import Category
from catalogs.models.models import Advert
from catalogs.permissions import IsOwner
from catalogs.serializers import CategoryListSerializer
from catalogs.serializers.serializers import (
    CategorySerializer,
    AdvertListSerializer,
    AdvertRetrieveSerializer,
    AdvertCreateSerializer,
    AdvertUpdateSerializer,
    ImageMultipleCreateSerializer,
)


@extend_schema(tags=['Catalog'])
@extend_schema_view(
    multiple_create=extend_schema(
        summary='Create multiple images.',
        description='Create multiple images. Main image can be only single and extra images can be several for a '
        'advert.',
    )
)
class ImageViewSet(viewsets.ModelViewSet):
    serializer_classes = dict(
        multiple_create=ImageMultipleCreateSerializer,
    )
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        return self.serializer_classes[self.action]

    @action(['post'], detail=False)
    def multiple_create(self, request):
        data = request.data
        data = {key: data[key] if len(data.getlist(key)) == 1 else data.getlist(key) for key in data.keys()}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


@extend_schema(tags=['Catalog'])
@extend_schema_view(
    list=extend_schema(summary='Get an advert list.'),
    retrieve=extend_schema(summary='Get an advert by ID.'),
    create=extend_schema(summary='Create a new advert.'),
    update=extend_schema(summary='Update an advert by ID fully.'),
    partial_update=extend_schema(summary='Update an advert by ID partially.'),
    destroy=extend_schema(summary='Delete an advert by ID with a related address.'),
)
class AdvertViewSet(viewsets.ModelViewSet):
    queryset = Advert.objects.prefetch_related('address').order_by('-created_at')
    serializer_classes = dict(
        list=AdvertListSerializer,
        retrieve=AdvertRetrieveSerializer,
        create=AdvertCreateSerializer,
        update=AdvertUpdateSerializer,
    )

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return self.serializer_classes['update']
        return self.serializer_classes[self.action]

    def get_permissions(self):
        match self.action:
            case 'create':
                return (IsAuthenticated(),)
            case 'list' | 'retrieve':
                return (AllowAny(),)
            case _:
                return (IsOwner(),)


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
class CategoryViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_classes = dict(
        list=CategoryListSerializer,
        select_list=CategorySerializer,
    )
    permission_classes = (AllowAny,)
    queryset = Category.objects.filter(parent=None)

    def get_serializer_class(self):
        return self.serializer_classes[self.action]

    def get_queryset(self):
        if self.action == 'select_list':
            return Category.objects.filter(children=None)
        else:
            return super().get_queryset()

    @action(methods=['get'], detail=False)
    def select_list(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
