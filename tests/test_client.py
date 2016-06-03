import os
import json

import requests_mock
import unittest

from percy import client


class TestPercyClient(unittest.TestCase):

    def setUp(self):
        os.environ['PERCY_TOKEN'] = 'abcd1234'
        self.percy_client = client.Client()

    def test_default_connection(self):
        self.assertNotEqual(self.percy_client.get_connection(), None)

    @requests_mock.Mocker()
    def test_create_build(self, mock):
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'build_response.json')
        mock_data = open(fixture_path).read()
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=mock_data)
        build_data = self.percy_client.create_build(repo='foo/bar')
        assert build_data == json.loads(mock_data)
