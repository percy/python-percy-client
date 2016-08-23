import os
import requests_mock
import unittest
import percy
from percy import connection


class TestPercyConnection(unittest.TestCase):
    def setUp(self):
        self.percy_connection = connection.Connection(percy.Config(access_token='foo'))

    @requests_mock.Mocker()
    def test_get(self, mock):
        mock.get('http://api.percy.io', text='{"data":"GET Percy"}')
        data = self.percy_connection.get('http://api.percy.io')
        self.assertEqual(data['data'], 'GET Percy')

        auth_header = mock.request_history[0].headers['Authorization']
        assert auth_header == 'Token token=foo'

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

    # @requests_mock.Mocker()
    # def test_post_error(self, mock):
    #     mock.post('http://api.percy.io', text='{"error":"foo"}', status_code=500)
    #     try:
    #         data = self.percy_connection.post(
    #             'http://api.percy.io',
    #             data='{"data": "data"}'
    #         )
    #     except:
    #         return
    #     else:
    #         raise Exception('Error not raised')
