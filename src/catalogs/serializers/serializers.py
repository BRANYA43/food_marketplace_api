from rest_framework import serializers

from catalogs.models import Category
from catalogs.models.models import Advert


class AdvertListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = ('id', 'name', 'category', 'price')
        read_only_fields = fields


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class CategoryListSerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField('get_children')

    class Meta:
        model = Category
        fields = ('id', 'name', 'sub_categories')

    def get_children(self, obj):
        if obj.children.exists():
            return self.__class__(obj.children.all(), many=True).data
        return []
