from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from utils.tests import APITestCase

from accounts import permissions


User = get_user_model()


class IsCurrentUserPermissionTest(APITestCase):
    def setUp(self) -> None:
        self.permission = permissions.IsCurrentUser()
        self.request = self.request_factory.get('/')
        self.anonymous = AnonymousUser()
        self.owner = self.create_test_user()
        self.not_owner = self.create_test_user('not.owner@test.come')

    def test_permission_doesnt_passes_unauthenticated_user(self):
        self.request.user = self.anonymous
        self.assertFalse(self.permission.has_permission(self.request, None))

    def test_permission_doesnt_passes_authenticated_user_who_doesnt_own_current_account(self):
        self.request.user = self.not_owner
        self.assertTrue(self.permission.has_permission(self.request, None))
        self.assertFalse(self.permission.has_object_permission(self.request, None, self.owner))

    def test_permission_passes_authenticated_user_who_own_current_account(self):
        self.request.user = self.owner
        self.assertTrue(self.permission.has_permission(self.request, None))
        self.assertTrue(self.permission.has_object_permission(self.request, None, self.owner))


class IsUnauthenticatedPermissionTest(APITestCase):
    def setUp(self) -> None:
        self.permission = permissions.IsUnauthenticated()
        self.request = self.request_factory.get('/')
        self.request.user = AnonymousUser()

    def test_permission_passes_unauthenticated_user(self):
        self.assertTrue(self.permission.has_permission(self.request, None))

    def test_permission_doesnt_pass_authenticated_user(self):
        self.request.user = self.create_test_user()
        self.assertFalse(self.permission.has_permission(self.request, None))
