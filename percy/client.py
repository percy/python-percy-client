# -*- coding: utf-8 -*-
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
        repo = kwargs.get('repo', self.environment.repo)
        branch = kwargs.get('branch', self.environment.branch)
        pull_request_number = kwargs.get(
            'pull_request_number',
            self.environment.pull_request_number
        )
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
            repo=repo
        )
        build_data = self._connection.post(path=path, data=data)
        return build_data
