from rest_framework import serializers

from catalogs import models


class AdvertAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdvertAddress
        fields = ('advert', 'region', 'city', 'village', 'street', 'number')
        extra_kwargs = dict(advert=dict(required=False, write_only=True))

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.full_clean()
        instance.save()
        return instance

    def create(self, validated_data):
        instance = models.AdvertAddress(**validated_data)
        instance.full_clean()
        instance.save()
        return instance


class _RecurseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class CategoryListSerializer(serializers.ModelSerializer):
    children = _RecurseSerializer(many=True)

    class Meta:
        model = models.Category
        fields = ('id', 'name', 'children')


class CategoryRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = (
            'id',
            'name',
        )
