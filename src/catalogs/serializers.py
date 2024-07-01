from rest_framework import serializers

from catalogs import models


class _RecurseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class CategoryListSerializer(serializers.ModelSerializer):
    children = _RecurseSerializer(many=True)

    class Meta:
        model = models.Category
        fields = ('slug', 'name', 'children')


class CategoryRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = (
            'slug',
            'name',
        )
