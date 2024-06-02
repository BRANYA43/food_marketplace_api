from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APITestCase

from accounts import permissions


User = get_user_model()


class IsUnauthenticatedPermissionTest(APITestCase):
    def setUp(self) -> None:
        self.permission = permissions.IsUnauthenticated()

    def get_mock_request(self, user=AnonymousUser()):
        request = MagicMock()
        request.user = user
        return request

    def test_permission_passes_unauthenticated_user(self):
        request = self.get_mock_request()
        self.assertTrue(self.permission.has_permission(request, None))

    def test_permission_doesnt_pass_authenticated_user(self):
        user = User.objects.create_user(email='test@test.com', password='qwe123!@#')
        request = self.get_mock_request(user)
        self.assertFalse(self.permission.has_permission(request, None))
