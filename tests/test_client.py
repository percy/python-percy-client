import os
import json

import requests_mock
import unittest

import percy


class TestPercyClient(unittest.TestCase):

    def setUp(self):
        os.environ['PERCY_TOKEN'] = 'abcd1234'
        self.percy_client = percy.Client()

    def test_default_connection(self):
        self.assertNotEqual(self.percy_client.get_connection(), None)

    @requests_mock.Mocker()
    def test_create_build(self, mock):
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'build_response.json')
        build_fixture = open(fixture_path).read()
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=build_fixture)

        build_data = self.percy_client.create_build(repo='foo/bar')
        assert build_data == json.loads(build_fixture)

    @requests_mock.Mocker()
    def test_create_snapshot(self, mock):
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'build_response.json')
        build_fixture = open(fixture_path).read()
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=build_fixture)
        build_id = json.loads(build_fixture)['data']['id']

        resources = [
            percy.Resource(resource_url='/', is_root=True, content='foo'),
        ]

        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'build_response.json')
        mock_data = open(fixture_path).read()
        mock.post('https://percy.io/api/v1/builds/{0}/snapshots/'.format(build_id), text=mock_data)

        build_data = self.percy_client.create_build(repo='foo/bar')
        snapshot_data = self.percy_client.create_snapshot(build_id, resources)

        assert snapshot_data == json.loads(mock_data)

    @requests_mock.Mocker()
    def test_finalize_snapshot(self, mock):
        mock.post('https://percy.io/api/v1/snapshots/123/finalize', text='{"success":true}')
        self.assertEqual(self.percy_client.finalize_snapshot(123)['success'], True)
