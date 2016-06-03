# -*- coding: utf-8 -*-
import hashlib
import base64

from connection import Connection
from environment import Environment
from config import Config

__all__ = ['Client']


class Client(object):

    def __init__(self, connection=None):
        self.environment = Environment()
        self.config = Config()
        if connection:
            self._connection = connection
        else:
            self._connection = Connection(self.config)

    def get_connection(self):
        return self._connection

    def create_build(self, **kwargs):
        repo = kwargs.get('repo') or self.environment.repo
        branch = kwargs.get('branch') or self.environment.branch
        pull_request_number = kwargs.get('pull_request_number') \
          or self.environment.pull_request_number

        data = {
            'data': {
                'type': 'builds',
                'attributes': {
                    'branch': branch,
                    'pull-request-number': pull_request_number,
                }
            }
        }
        path = "{base_url}/repos/{repo}/builds/".format(
            base_url=self.config.api_url,
            repo=repo,
        )
        return self._connection.post(path=path, data=data)

    def create_snapshot(self, build_id, resources, **kwargs):
        if len(resources) <= 0:
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
                'relationship': {
                    'resources': {
                        'data': resources.map(lambda r: r.serialize())
                    }
                }
            }
        }
        path = "{base_url}/builds/{build_id}/snapshots/".format(
            base_url=self.config.api_url,
            build_id=build_id
        )
        return self._connection.post(path=path, data=data)

    def upload_resource(self, build_id, content):
        sha = hashlib.sha256(content).hexdigest()
        data = {
            'data': {
                'type': 'resources',
                'attributes': {
                    'id': sha,
                    'base64-content': base64.b64encode(content)
                }

            }
        }
        path = "{base_url}/builds/{build_id}/resources/".format(
            base_url=self.config.api_url,
            build_id=build_id
        )
        return self._connection.post(path=path, data=data)
