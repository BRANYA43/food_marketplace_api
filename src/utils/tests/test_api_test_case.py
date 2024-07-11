from unittest.mock import MagicMock, patch

from utils.tests import ApiTestCase


class ApiTestCaseTest(ApiTestCase):
    def test_assert_is_subclass(self):
        class Parent:
            pass

        class Children(Parent):
            pass

        class Another:
            pass

        self.assert_is_subclass(Children, Parent)  # not raise

        with self.assertRaisesRegex(
            AssertionError,
            rf'{Another} is not subclass of {Parent}.',
        ):
            self.assert_is_subclass(Another, Parent)

    def test_assert_response_status(self):
        mock_response = MagicMock(status_code=200)
        self.assert_response_status(mock_response, 200)  # not raise

        with self.assertRaisesRegex(
            AssertionError, rf'Expected response status code "300", but got "{mock_response.status_code}".'
        ):
            self.assert_response_status(mock_response, 300)

    @patch('rest_framework.test.APIClient.get')
    def test_assert_allowed_method(self, mock_client_get: MagicMock):
        mock_response = MagicMock(status_code=200)
        mock_client_get.return_value = mock_response
        url = '/'

        self.assert_allowed_method(url, 'get', 200)  # not raise

        with self.assertRaisesRegex(
            AssertionError, rf'Expected response status code "300", but got "{mock_response.status_code}".'
        ):
            self.assert_allowed_method(url, 'get', 300)

        mock_response.status_code = 405
        with self.assertRaisesRegex(AssertionError, r'Expected method "get" is not allowed.'):
            self.assert_allowed_method(url, 'get', 200)

    @patch('rest_framework.test.APIClient.get')
    def test_assert_not_allowed_methods(self, mock_client_get):
        mock_response = MagicMock(status_code=405)
        mock_client_get.return_value = mock_response
        url = '/'

        self.assert_not_allowed_methods(url, ['get'])  # not raise

        mock_response.status_code = 200
        with self.assertRaisesRegex(
            AssertionError, rf'Expected response status code "405", but got "{mock_response.status_code}".'
        ):
            self.assert_not_allowed_methods(url, ['get'])
