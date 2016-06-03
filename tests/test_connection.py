from percy import connection
import requests_mock
import unittest


class TestPercyConnection(unittest.TestCase):
    def setUp(self):
        self.percy_connection = connection.Connection()

    @requests_mock.Mocker()
    def test_get(self, mock):
        mock.get('http://api.percy.io', text='{"data":"GET Percy"}')
        data = self.percy_connection.get('http://api.percy.io')
        self.assertEqual(data['data'], 'GET Percy')

    @requests_mock.Mocker()
    def test_post(self, mock):
        mock.post('http://api.percy.io', text='{"data":"POST Percy"}')
        data = self.percy_connection.post(
            'http://api.percy.io',
            data='{"data": "data"}'
        )
        self.assertEqual(data['data'], 'POST Percy')
