from rest_framework.routers import DefaultRouter

from catalogs import views

router = DefaultRouter()
router.register('category', views.CategoryViewSet)

urlpatterns: list = []
urlpatterns += router.urls
