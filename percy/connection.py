import requests


class Connection(object):
    def __init__(self, config):
        self.config = config

    def _token_header(self):
        return "Token token={0}".format(self.config.access_token)

    def get(self, path, options={}):
        headers = {
            'Authorization': self._token_header(),
        }
        response = requests.get(path, headers=headers)
        # Exception handling TODO
        return response.json()

    def post(self, path, data, options={}):
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Authorization': self._token_header(),
        }
        response = requests.post(path, json=data, headers=headers)
        return response.json()
