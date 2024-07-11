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


class AdvertSerializer(serializers.ModelSerializer):
    address = AdvertAddressSerializer(required=False)

    class Meta:
        model = models.Advert
        fields = (
            'id',
            'user',
            'category',
            'title',
            'descr',
            'price',
            'address',
            'use_pickup',
            'use_nova_post',
            'use_courier',
        )
        read_only_field = ('id',)

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        advert = models.Advert(**validated_data)
        advert.full_clean()
        advert.save()

        if address_data is not None:
            self._update_or_create_address(advert, address_data)

        advert.refresh_from_db()
        return advert

    def update(self, instance, validated_data):
        advert = instance
        address_data = validated_data.pop('address', None)
        for field, value in validated_data.items():
            setattr(advert, field, value)
        advert.full_clean()
        advert.save()

        if address_data is not None:
            self._update_or_create_address(advert, address_data)

        advert.refresh_from_db()
        return advert

    def _update_or_create_address(self, advert, address_data):
        if (address := getattr(advert, 'address', None)) is not None:
            serializer = AdvertAddressSerializer(address, address_data, partial=True)
        else:
            address_data['advert'] = advert.pk
            serializer = AdvertAddressSerializer(data=address_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()


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
