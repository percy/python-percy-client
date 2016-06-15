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


class TestRunner(unittest.TestCase):
    def test_init(self):
        runner = percy.Runner()
        self.assertEqual(runner.client.config.default_widths, [])
        runner = percy.Runner(config=percy.Config(default_widths=(1280, 375)))
        self.assertEqual(runner.client.config.default_widths, (1280, 375))

    @requests_mock.Mocker()
    def test_auth_error(self, mock):
        runner = percy.Runner()
        self.assertRaises(errors.AuthError, lambda: runner.initialize_build())

    @requests_mock.Mocker()
    def test_initialize_build(self, mock):
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
                    'missing-resources': {},
                },
            },
        }
        mock.post('https://percy.io/api/v1/repos/foo/bar/builds/', text=json.dumps(build_fixture))
        runner.initialize_build(repo='foo/bar')

        # Whitebox check that the current build data is set correctly.
        self.assertEqual(runner._current_build, build_fixture)

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


    @requests_mock.Mocker()
    def test_snapshot(self, mock):
        runner = percy.Runner()
        self.assertRaises(errors.UninitializedBuildError, lambda: runner.snapshot('foo'))

    def test_finalize_build(self):
        pass
