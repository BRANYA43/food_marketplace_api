from rest_framework.routers import DefaultRouter

from catalogs import views

router = DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('adverts', views.AdvertViewSet)

urlpatterns: list = []
urlpatterns += router.urls
