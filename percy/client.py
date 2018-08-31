# -*- coding: utf-8 -*-

from percy.connection import Connection
from percy.environment import Environment
from percy.config import Config
from percy import utils

__all__ = ['Client']


class Client(object):

    def __init__(self, connection=None, config=None, environment=None):
        self._environment = environment if environment else Environment()
        self._config = config if config else Config()
        self._connection = connection if connection else Connection(self._config, self._environment)

    @property
    def connection(self):
        return self._connection

    @property
    def config(self):
        return self._config

    @property
    def environment(self):
        return self._environment

    def create_build(self, **kwargs):
        branch = kwargs.get('branch') or self.environment.branch
        pull_request_number = kwargs.get('pull_request_number') \
            or self.environment.pull_request_number
        resources = kwargs.get('resources')
        parallel_nonce = kwargs.get('parallel_nonce') or self.environment.parallel_nonce
        parallel_total_shards = kwargs.get('parallel_total_shards') \
            or self.environment.parallel_total_shards

        # Only pass parallelism data if it all exists.
        if not parallel_nonce or not parallel_total_shards:
            parallel_nonce = None
            parallel_total_shards = None

        commit_data = kwargs.get('commit_data') or self.environment.commit_data;

        data = {
            'data': {
                'type': 'builds',
                'attributes': {
                    'branch': branch,
                    'target-branch': self.environment.target_branch,
                    'target-commit-sha': self.environment.target_commit_sha,
                    'commit-sha': commit_data['sha'],
                    'commit-committed-at': commit_data['committed_at'],
                    'commit-author-name': commit_data['author_name'],
                    'commit-author-email': commit_data['author_email'],
                    'commit-committer-name': commit_data['committer_name'],
                    'commit-committer-email': commit_data['committer_email'],
                    'commit-message': commit_data['message'],
                    'pull-request-number': pull_request_number,
                    'parallel-nonce': parallel_nonce,
                    'parallel-total-shards': parallel_total_shards,
                }
            }
        }

        if resources:
            data['data']['relationships'] = {
                'resources': {
                    'data': [r.serialize() for r in resources],
                }
            }

        path = "{base_url}/builds/".format(base_url=self.config.api_url)

        return self._connection.post(path=path, data=data)

    def finalize_build(self, build_id):
        path = "{base_url}/builds/{build_id}/finalize".format(
            base_url=self.config.api_url,
            build_id=build_id,
        )
        return self._connection.post(path=path, data={})

    def create_snapshot(self, build_id, resources, **kwargs):
        if not resources or len(resources) <= 0:
            raise ValueError(
                'resources should be an array of Percy.Resource objects'
            )
        widths = kwargs.get('widths', self.config.default_widths)
        data = {
            'data': {
                'type': 'snapshots',
                'attributes': {
                    'name': kwargs.get('name'),
                    'enable-javascript': kwargs.get('enable_javascript'),
                    'widths': widths,
                },
                'relationships': {
                    'resources': {
                        'data': [r.serialize() for r in resources],
                    }
                }
            }
        }
        path = "{base_url}/builds/{build_id}/snapshots/".format(
            base_url=self.config.api_url,
            build_id=build_id
        )
        return self._connection.post(path=path, data=data)

    def finalize_snapshot(self, snapshot_id):
        path = "{base_url}/snapshots/{snapshot_id}/finalize".format(
            base_url=self.config.api_url,
            snapshot_id=snapshot_id
        )
        return self._connection.post(path=path, data={})

    def upload_resource(self, build_id, content):
        sha = utils.sha256hash(content)
        data = {
            'data': {
                'type': 'resources',
                'id': sha,
                'attributes': {
                    'base64-content': utils.base64encode(content),
                }

            }
        }
        path = "{base_url}/builds/{build_id}/resources/".format(
            base_url=self.config.api_url,
            build_id=build_id
        )
        return self._connection.post(path=path, data=data)
