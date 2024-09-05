from rest_framework.routers import DefaultRouter

from catalogs import views

router = DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('adverts', views.AdvertViewSet)
router.register('images', views.ImageViewSet, 'images')

urlpatterns: list = []
urlpatterns += router.urls
