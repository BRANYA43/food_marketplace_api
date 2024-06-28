from rest_framework import serializers

from catalogs import models


class _FilterListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class _RecurseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class CategoryListSerializer(serializers.ModelSerializer):
    children = _RecurseSerializer(many=True)

    class Meta:
        model = models.Category
        fields = ('slug', 'name', 'children')
        list_serializer_class = _FilterListSerializer
