from rest_framework.routers import DefaultRouter

from accounts import views

router = DefaultRouter()
router.register('user', views.UserViewSet)

urlpatterns: list = []
urlpatterns += router.urls
