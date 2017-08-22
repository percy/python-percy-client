import requests
from percy.user_agent import UserAgent
from percy import utils

class Connection(object):
    def __init__(self, config, environment):
        self.config = config
        self.user_agent = str(UserAgent(config, environment))

    def _token_header(self):
        return "Token token={0}".format(self.config.access_token)

    def get(self, path, options={}):
        headers = {
            'Authorization': self._token_header(),
            'User-Agent': self.user_agent,
        }
        response = requests.get(path, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            utils.print_error('Received a {} error requesting: {}'.format(response.status_code, path))
            utils.print_error(response.content)
            raise e
        return response.json()

    def post(self, path, data, options={}):
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Authorization': self._token_header(),
            'User-Agent': self.user_agent,
        }
        response = requests.post(path, json=data, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            utils.print_error('Received a {} error posting to: {}.'.format(response.status_code, path))
            utils.print_error(response.content)
            raise e
        return response.json()
