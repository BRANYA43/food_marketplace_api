from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from catalogs.models import Category
from catalogs.models.models import Advert, Image
from utils.serializers import AddressFieldSerializer
from utils.serializers.mixins import AddressCreateUpdateMixin


class ImageMultipleCreateSerializer(serializers.ModelSerializer):
    files = serializers.ListSerializer(
        child=serializers.ImageField(allow_null=False, allow_empty_file=False, required=True),
        allow_empty=False,
        allow_null=False,
        required=True,
    )
    types = serializers.ListSerializer(
        child=serializers.ChoiceField(choices=Image.Type.choices, allow_null=False, required=True),
        allow_empty=False,
        allow_null=False,
        required=True,
    )

    class Meta:
        model = Image
        fields = ('advert', 'files', 'types')

    def validate(self, attrs):
        files = attrs.get('files', [])
        types = attrs.get('types', [None])

        if len(files) != len(types):
            raise ValidationError(
                'File quantity should match type quantity.',
                'invalid_quantity',
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        advert = validated_data.pop('advert')
        image_data = [dict(advert=advert, file=file, type=type_) for file, type_ in zip(*validated_data.values())]

        for data in image_data:
            img = Image(**data)
            img.full_clean()
            img.save()

        return Image.objects.filter(advert=advert).first()


class AdvertListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = ('id', 'name', 'category', 'price')
        read_only_fields = fields


class AdvertRetrieveSerializer(serializers.ModelSerializer):
    address = AddressFieldSerializer(read_only=True)

    class Meta:
        model = Advert
        fields = (
            'id',
            'owner',
            'category',
            'name',
            'descr',
            'price',
            'quantity',
            'pickup',
            'nova_post',
            'courier',
            'address',
        )
        read_only_fields = fields


class AdvertCreateSerializer(AddressCreateUpdateMixin, serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = (
            'id',
            'owner',
            'category',
            'name',
            'descr',
            'price',
            'quantity',
            'pickup',
            'nova_post',
            'courier',
            'address',
        )
        read_only_fields = ('id',)


class AdvertUpdateSerializer(AddressCreateUpdateMixin, serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = (
            'id',
            'owner',
            'category',
            'name',
            'descr',
            'price',
            'quantity',
            'pickup',
            'nova_post',
            'courier',
            'address',
        )
        read_only_fields = ('id', 'owner')


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
