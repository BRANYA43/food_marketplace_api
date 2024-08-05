from unittest.mock import patch, MagicMock

from utils.tests.cases.view_test_case import ViewTestCase


class ViewTestCaseTest(ViewTestCase):
    url = '/'

    @patch('rest_framework.test.APIClient.get', return_value=MagicMock(status_code=200))
    def test_assert_http_methods_availability(self, mock_client_get: MagicMock):
        self.assert_http_methods_availability(self.url, ['get'], 200)  # not raise

        with self.assertRaisesRegex(AssertionError, r'Expected the response status code "300", but got "200".'):
            self.assert_http_methods_availability(self.url, ['get'], 300)

    def test_assert_response(self):
        mock_response = MagicMock(status_code=200, data=None)

        self.assert_response(mock_response, 200)  # not raise
        self.assert_response(mock_response, 200, output_data=None)  # not raise

        with self.assertRaisesRegex(AssertionError, r'Expected the response status code "300", but got "200".'):
            self.assert_response(mock_response, 300)

        with self.assertRaisesRegex(AssertionError, r'None !='):
            self.assert_response(mock_response, 200, output_data={'test': 'test'})
