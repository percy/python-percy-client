import os

import requests_mock
import unittest

from percy import connection
from percy import config


class TestPercyConnection(unittest.TestCase):
    def setUp(self):
        os.environ['PERCY_TOKEN'] = 'abcd1234'
        self.percy_connection = connection.Connection(config.Config())

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
