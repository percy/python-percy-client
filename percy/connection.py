import requests


class Connection(object):
    def __init__(self, config):
        self.config = config

    def get(self, path, options={}):
        headers = {
            'Authentication': "Token token={0}".format(self.config.access_token)
        }
        response = requests.get(path, headers=headers)
        # Exception handling TODO
        return response.json()

    def post(self, path, data, options={}):
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Authentication': "Token token={0}".format(self.config.access_token)
        }
        response = requests.post(path, data=data, headers=headers)
        return response.json()
