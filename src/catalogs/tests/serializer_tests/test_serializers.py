from catalogs.models import Category
from catalogs.serializers import CategoryListSerializer
from catalogs.serializers.serializers import CategorySerializer
from utils.tests import ApiTestCase


class CategorySerializerTest(ApiTestCase):
    serializer_class = CategorySerializer
    model = Category

    def test_serializer_returns_expected_data_for_some_category(self):
        self.create_test_category(name='Category 1')
        self.create_test_category(name='Category 2')

        expected_data = [dict(id=category.id, name=category.name) for category in self.model.objects.all()]

        serializer = self.serializer_class(self.model.objects.filter(children=None), many=True)

        self.assertSequenceEqual(serializer.data, expected_data)

    def test_serializer_returns_expected_data_for_category(self):
        category = self.create_test_category(name='Category 1')

        expected_data = dict(id=category.id, name=category.name)

        serializer = self.serializer_class(category)

        self.assertSequenceEqual(serializer.data, expected_data)


class CategoryListSerializerTest(ApiTestCase):
    serializer_class = CategoryListSerializer
    model = Category

    def get_expected_category_data(self, categories):
        ret = []
        for category in categories:
            ret.append(
                dict(
                    id=category.id,
                    name=category.name,
                    sub_categories=self.get_expected_category_data(category.children.all()),
                )
            )
        return ret

    def test_serializer_returns_expected_data_for_some_categories(self):
        self.create_test_category(name='Category 1')
        self.create_test_category(name='Category 2')
        self.create_test_category(name='Category 3')

        expected_data = self.get_expected_category_data(self.model.objects.filter(parent=None))

        serializer = self.serializer_class(self.model.objects.filter(parent=None), many=True)

        self.assertSequenceEqual(serializer.data, expected_data)

    def test_serializer_returns_expected_data_for_some_categories_with_children(self):
        food = self.create_test_category(name='Food')
        vegetables = self.create_test_category(name='Vegetables', parent=food)
        self.create_test_category(name='Tomato', parent=vegetables)
        self.create_test_category(name='Fruits', parent=food)
        self.create_test_category('All For Home')

        expected_data = self.get_expected_category_data(self.model.objects.filter(parent=None))

        serializer = self.serializer_class(self.model.objects.filter(parent=None), many=True)

        self.assertSequenceEqual(serializer.data, expected_data)
