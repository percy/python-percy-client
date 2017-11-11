import os
import requests
import requests_mock
import unittest
import percy
from percy import connection


class TestPercyConnection(unittest.TestCase):
    def setUp(self):
        config = percy.Config(access_token='foo')
        environment = percy.Environment()

        self.percy_connection = connection.Connection(config, environment)

    @requests_mock.Mocker()
    def test_get(self, mock):
        mock.get('http://api.percy.io', text='{"data":"GET Percy"}')
        data = self.percy_connection.get('http://api.percy.io')
        self.assertEqual(data['data'], 'GET Percy')

        auth_header = mock.request_history[0].headers['Authorization']
        assert auth_header == 'Token token=foo'

    # TODO: This test fails, because requests_mock replaces the adapter where the
    # retry configuration is injected. Can we find a different way to supply mock responses?
    # @requests_mock.Mocker()
    # def test_get_error_is_retried(self, mock):
    #     mock.get('http://api.percy.io', [{'text':'{"error":"foo"}', 'status_code':503},
    #         {'text':'{"data":"GET Percy"}', 'status_code':200}])
    #     data = self.percy_connection.get('http://api.percy.io')
    #     self.assertEqual(data['data'], 'GET Percy')

    @requests_mock.Mocker()
    def test_get_error(self, mock):
        mock.get('http://api.percy.io', text='{"error":"foo"}', status_code=401)
        self.assertRaises(requests.exceptions.HTTPError, lambda: self.percy_connection.get(
            'http://api.percy.io'
        ))

    @requests_mock.Mocker()
    def test_post(self, mock):
        mock.post('http://api.percy.io', text='{"data":"POST Percy"}')
        data = self.percy_connection.post(
            'http://api.percy.io',
            data='{"data": "data"}'
        )
        self.assertEqual(data['data'], 'POST Percy')

        auth_header = mock.request_history[0].headers['Authorization']
        assert auth_header == 'Token token=foo'

    @requests_mock.Mocker()
    def test_post_error(self, mock):
        mock.post('http://api.percy.io', text='{"error":"foo"}', status_code=500)
        self.assertRaises(requests.exceptions.HTTPError, lambda: self.percy_connection.post(
            'http://api.percy.io',
            data='{"data": "data"}'
        ))
