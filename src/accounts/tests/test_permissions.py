from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from utils.tests import APITestCase

from accounts import permissions


User = get_user_model()


class IsUnauthenticatedPermissionTest(APITestCase):
    def setUp(self) -> None:
        self.permission = permissions.IsUnauthenticated()
        self.request = self.request_factory.get('/')
        self.request.user = AnonymousUser()

    def test_permission_passes_unauthenticated_user(self):
        self.assertTrue(self.permission.has_permission(self.request, None))

    def test_permission_doesnt_pass_authenticated_user(self):
        user = User.objects.create_user(email='test@test.com', password='qwe123!@#')
        self.request.user = user
        self.assertFalse(self.permission.has_permission(self.request, None))
