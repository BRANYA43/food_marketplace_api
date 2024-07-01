from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from catalogs import models, serializers


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Category.objects.filter(parent=None).order_by('name')
    serializer_classes = dict(
        list=serializers.CategoryListSerializer,
        retrieve=serializers.CategoryRetrieveSerializer,
    )
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        return self.serializer_classes[self.action]
