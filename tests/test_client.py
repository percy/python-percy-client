import base64
import hashlib
import json
import os
import unittest

import requests_mock
import percy
from percy import utils

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestPercyClient(unittest.TestCase):

    def setUp(self):
        percy_config = percy.Config(access_token='abcd1234', default_widths=[1280, 375])
        self.percy_client = percy.Client(config=percy_config)

    def test_defaults(self):
        self.assertNotEqual(self.percy_client.connection, None)
        self.assertNotEqual(self.percy_client.config, None)
        self.assertNotEqual(self.percy_client.environment, None)

    def test_config_variables(self):
        self.assertEqual(self.percy_client.config.default_widths, [1280, 375])
        self.percy_client.config.default_widths = [640, 480]
        self.assertEqual(self.percy_client.config.default_widths, [640, 480])

    @requests_mock.Mocker()
    def test_create_build(self, mock):
        fixture_path = os.path.join(FIXTURES_DIR, 'build_response.json')
        build_fixture = open(fixture_path).read()
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=build_fixture)
        resources = [
            percy.Resource(resource_url='/main.css', is_root=False, content='foo'),
        ]

        build_data = self.percy_client.create_build(repo='foo/bar', resources=resources)
        assert mock.request_history[0].json() == {
            'data': {
                'type': 'builds',
                'attributes': {
                    'branch': self.percy_client.environment.branch,
                    'commit-sha': self.percy_client.environment.commit_sha,
                    'pull-request-number': self.percy_client.environment.pull_request_number,
                    'parallel-nonce': self.percy_client.environment.parallel_nonce,
                    'parallel-total-shards': self.percy_client.environment.parallel_total_shards,
                },
               'relationships': {
                    'resources': {
                        'data': [
                            {
                                'type': 'resources',
                                'id': resources[0].sha,
                                'attributes': {
                                    'resource-url': resources[0].resource_url,
                                    'mimetype': resources[0].mimetype,
                                    'is-root': resources[0].is_root,
                                }
                            }
                        ],
                    }
                }

            }
        }
        assert build_data == json.loads(build_fixture)

    @requests_mock.Mocker()
    def test_finalize_build(self, mock):
        fixture_path = os.path.join(FIXTURES_DIR, 'build_response.json')
        build_fixture = open(fixture_path).read()
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=build_fixture)
        mock.post('https://percy.io/api/v1/builds/31/finalize', text='{"success": "true"}')

        build_data = self.percy_client.create_build(repo='foo/bar')
        build_id = build_data['data']['id']
        finalize_response = self.percy_client.finalize_build(build_id=build_id)

        assert mock.request_history[1].json() == {}
        assert finalize_response == {'success': 'true'}

    @requests_mock.Mocker()
    def test_create_snapshot(self, mock):
        fixture_path = os.path.join(FIXTURES_DIR, 'build_response.json')
        build_fixture = open(fixture_path).read()
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=build_fixture)
        build_id = json.loads(build_fixture)['data']['id']

        resources = [
            percy.Resource(resource_url='/', is_root=True, content='foo'),
        ]

        fixture_path = os.path.join(FIXTURES_DIR, 'snapshot_response.json')
        mock_data = open(fixture_path).read()
        mock.post('https://percy.io/api/v1/builds/{0}/snapshots/'.format(build_id), text=mock_data)

        build_data = self.percy_client.create_build(repo='foo/bar')
        snapshot_data = self.percy_client.create_snapshot(
            build_id,
            resources,
            name='homepage',
            widths=[1280],
            enable_javascript=True,
        )

        assert mock.request_history[1].json() == {
            'data': {
                'type': 'snapshots',
                'attributes': {
                    'name': 'homepage',
                    'enable-javascript': True,
                    'widths': [1280],
                },
                'relationships': {
                    'resources': {
                        'data': [
                            {
                                'type': 'resources',
                                'id': resources[0].sha,
                                'attributes': {
                                    'resource-url': resources[0].resource_url,
                                    'mimetype': resources[0].mimetype,
                                    'is-root': resources[0].is_root,
                                }
                            }
                        ],
                    }
                }
            }
        }
        assert snapshot_data == json.loads(mock_data)

    @requests_mock.Mocker()
    def test_finalize_snapshot(self, mock):
        mock.post('https://percy.io/api/v1/snapshots/123/finalize', text='{"success":true}')
        self.assertEqual(self.percy_client.finalize_snapshot(123)['success'], True)
        assert mock.request_history[0].json() == {}

    @requests_mock.Mocker()
    def test_upload_resource(self, mock):
        mock.post('https://percy.io/api/v1/builds/123/resources/', text='{"success": "true"}')

        content = 'foo'
        result = self.percy_client.upload_resource(build_id=123, content=content)

        assert mock.request_history[0].json() == {
            'data': {
                'type': 'resources',
                'id': utils.sha256hash(content),
                'attributes': {
                    'base64-content': utils.base64encode(content)
                }

            }
        }
        assert result == {'success': 'true'}
