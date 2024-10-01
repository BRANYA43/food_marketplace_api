from typing import Optional

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from catalogs.models import Category
from catalogs.models.models import Advert, Image


class ImageMultipleDeleteSerializer(serializers.ModelSerializer):
    files = serializers.ListSerializer(
        child=serializers.CharField(allow_null=False, allow_blank=False, required=False),
        allow_empty=False,
        allow_null=False,
        required=True,
    )

    class Meta:
        model = Image
        fields = ('advert', 'files')

    def validate(self, attrs):
        advert = attrs['advert']
        files = set(attrs['files'])
        images = {str(img.file) for img in advert.images.filter(file__in=files)}
        if diff := files.difference(images):
            raise ValidationError(
                f'Advert have not followed images with the names: {list(diff)}.',
                'invalid_filename',
            )
        return attrs

    def delete(self):
        assert hasattr(self, '_errors'), 'You must call `.is_valid()` before calling `.save()`.'

        assert not self.errors, 'You cannot call `.save()` on a serializer with invalid data.'

        assert not hasattr(self, '_data'), (
            'You cannot call `.save()` after accessing `serializer.data`.'
            'If you need to access data before committing to the database then '
            "inspect 'serializer.validated_data' instead. "
        )

        advert = self.validated_data['advert']
        files = self.validated_data['files']
        advert.images.filter(file__in=files).delete()


class ImageMultipleCreateSerializer(serializers.ModelSerializer):
    files = serializers.ListSerializer(
        child=serializers.ImageField(allow_null=False, allow_empty_file=False, required=True),
        allow_empty=False,
        allow_null=False,
        required=True,
    )

    class Meta:
        model = Image
        fields = ('advert', 'files')

    @transaction.atomic
    def create(self, validated_data):
        advert = validated_data.pop('advert')
        image_data = [dict(advert=advert, file=file) for file in validated_data['files']]

        for data in image_data:
            img = Image(**data)
            img.full_clean()
            img.save()

        return img


class AdvertListSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField('get_main_image')

    class Meta:
        model = Advert
        fields = ('id', 'name', 'category', 'price', 'main_image')
        read_only_fields = fields

    @staticmethod
    def get_main_image(obj) -> Optional[str]:
        img = obj.images.filter(type=Image.Type.MAIN).first()
        if img is None:
            return None
        return str(img.file)


class AdvertRetrieveSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField('get_main_image')
    extra_images = serializers.SerializerMethodField('get_extra_images')

    class Meta:
        model = Advert
        fields = (
            'id',
            'owner',
            'category',
            'name',
            'descr',
            'price',
            'unit',
            'availability',
            'location',
            'delivery_methods',
            'delivery_comment',
            'payment_methods',
            'payment_card',
            'payment_comment',
            'main_image',
            'extra_images',
        )
        read_only_fields = fields

    @staticmethod
    def get_main_image(obj) -> Optional[str]:
        img = obj.images.filter(type=Image.Type.MAIN).first()
        if img is None:
            return None
        return str(img.file)

    @staticmethod
    def get_extra_images(obj) -> list[str]:
        imgs = obj.images.filter(type=Image.Type.EXTRA)
        return [str(img.file) for img in imgs]


class AdvertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = (
            'id',
            'owner',
            'category',
            'name',
            'descr',
            'price',
            'unit',
            'availability',
            'location',
            'delivery_methods',
            'delivery_comment',
            'payment_methods',
            'payment_card',
            'payment_comment',
        )
        read_only_fields = ('id',)


class AdvertUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = (
            'id',
            'owner',
            'category',
            'name',
            'descr',
            'price',
            'unit',
            'availability',
            'location',
            'delivery_methods',
            'delivery_comment',
            'payment_methods',
            'payment_card',
            'payment_comment',
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
