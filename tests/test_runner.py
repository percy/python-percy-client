import json
import os
import sys
import unittest

import percy
import pytest
import requests_mock
from percy import errors
from percy import utils

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), 'testdata')


class FakeWebdriver(object):
    page_source = 'page source'
    current_url = '/'


SIMPLE_BUILD_FIXTURE = {
    'data': {
        'id': '123',
        'type': 'builds',
        'relationships': {
            'self': '/api/v1/builds/123',
            'missing-resources': {},
        },
    },
}

SIMPLE_SNAPSHOT_FIXTURE = {
    'data': {
        'id': '256',
        'type': 'snapshots',
        'relationships': {
            'self': '/api/v1/snapshots/256',
            'missing-resources': {},
        },
    },
}

class TestRunner(unittest.TestCase):
    def test_init(self):
        runner = percy.Runner()
        assert runner.client.config.default_widths == []
        runner = percy.Runner(config=percy.Config(default_widths=[1280, 375]))
        assert runner.client.config.default_widths == [1280, 375]

    @requests_mock.Mocker()
    def test_safe_initialize_when_disabled(self, mock):
        runner = percy.Runner()
        assert runner._is_enabled == False
        runner.initialize_build()

    @requests_mock.Mocker()
    def test_initialize_build(self, mock):
        root_dir = os.path.join(TEST_FILES_DIR, 'static')
        loader = percy.ResourceLoader(root_dir=root_dir, base_url='/assets/')
        config = percy.Config(access_token='foo')
        runner = percy.Runner(config=config, loader=loader)

        response_text = json.dumps(SIMPLE_BUILD_FIXTURE)
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=response_text)
        runner.initialize_build(repo='foo/bar')

        # Whitebox check that the current build data is set correctly.
        assert runner._current_build == SIMPLE_BUILD_FIXTURE
        assert runner.build_id == SIMPLE_BUILD_FIXTURE['data']['id']

    @requests_mock.Mocker()
    def test_initialize_build_sends_missing_resources(self, mock):
        root_dir = os.path.join(TEST_FILES_DIR, 'static')
        loader = percy.ResourceLoader(root_dir=root_dir, base_url='/assets/')
        config = percy.Config(access_token='foo')
        runner = percy.Runner(config=config, loader=loader)

        build_fixture = {
            'data': {
                'id': '123',
                'type': 'builds',
                'relationships': {
                    'self': "/api/v1/snapshots/123",
                    'missing-resources': {
                        'data': [
                            {
                                'type': 'resources',
                                'id': loader.build_resources[0].sha,
                            },
                        ],
                    },
                },
            },
        }
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=json.dumps(build_fixture))
        mock.post('https://percy.io/api/v1/builds/123/resources/', text='{"success": true}')
        runner.initialize_build(repo='foo/bar')

        # Make sure the missing resources were uploaded. The mock above will not fail if not called.
        with open(loader.build_resources[0].local_path, 'r') as f:
            content = f.read()
        assert len(content) > 0
        assert mock.request_history[1].json() == {
            'data': {
                'type': 'resources',
                'id': loader.build_resources[0].sha,
                'attributes': {
                    'base64-content': utils.base64encode(content)
                },
            },
        }

    def test_safe_snapshot_when_disabled(self):
        runner = percy.Runner()
        assert runner._is_enabled == False
        runner.snapshot()

    @requests_mock.Mocker()
    def test_snapshot(self, mock):
        root_dir = os.path.join(TEST_FILES_DIR, 'static')
        webdriver = FakeWebdriver()
        loader = percy.ResourceLoader(root_dir=root_dir, base_url='/assets/', webdriver=webdriver)
        config = percy.Config(access_token='foo')
        runner = percy.Runner(config=config, loader=loader)

        response_text = json.dumps(SIMPLE_BUILD_FIXTURE)
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=response_text)
        runner.initialize_build(repo='foo/bar')

        # Plain snapshot without a missing resource.
        response_text = json.dumps(SIMPLE_SNAPSHOT_FIXTURE)
        mock.post('https://percy.io/api/v1/builds/123/snapshots/', text=response_text)
        mock.post('https://percy.io/api/v1/snapshots/256/finalize', text='{"success": true}')
        runner.snapshot()

        # Snapshot with a missing resource.
        response_text = json.dumps({
            'data': {
                'id': '256',
                'type': 'snapshots',
                'relationships': {
                    'self': '/api/v1/snapshots/256',
                    'missing-resources': {
                        'data': [
                            {
                                'type': 'resources',
                                'id': loader.snapshot_resources[0].sha,
                            },
                        ],
                    },
                },
            },
        })
        mock.post('https://percy.io/api/v1/builds/123/snapshots/', text=response_text)
        mock.post('https://percy.io/api/v1/builds/123/resources/', text='{"success": true}')
        mock.post('https://percy.io/api/v1/snapshots/256/finalize', text='{"success": true}')
        runner.snapshot(name='foo', enable_javascript=True, widths=[1280])

        # Assert that kwargs are passed through correctly to create_snapshot.
        assert mock.request_history[3].json()['data']['attributes'] == {
            'enable-javascript': True,
            'name': 'foo',
            'widths': [1280],
        }

        # Assert that the snapshot resource was uploaded correctly.
        assert mock.request_history[4].json() == {
            'data': {
                'type': 'resources',
                'id': loader.snapshot_resources[0].sha,
                'attributes': {
                    'base64-content': utils.base64encode(FakeWebdriver.page_source)
                },
            },
        }

    @requests_mock.Mocker()
    def test_finalize_build(self, mock):
        config = percy.Config(access_token='foo')
        runner = percy.Runner(config=config)

        self.assertRaises(errors.UninitializedBuildError, lambda: runner.finalize_build())

        response_text = json.dumps(SIMPLE_BUILD_FIXTURE)
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=response_text)
        runner.initialize_build(repo='foo/bar')

        mock.post('https://percy.io/api/v1/builds/123/finalize', text='{"success": true}')
        runner.finalize_build()
        assert mock.request_history[1].json() == {}

        # Whitebox check that the current build data is reset.
        assert runner._current_build == None

    def test_safe_finalize_when_disabled(self):
        runner = percy.Runner()
        assert runner._is_enabled == False
        runner.finalize_build()
