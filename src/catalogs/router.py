from rest_framework.routers import DefaultRouter

from catalogs.views import CategoryViewSet

router = DefaultRouter()
router.register('category', CategoryViewSet, 'category')
