import requests

from .errors import Error, PercyBadRequest, PercyQuotaExceeded

error_map = {
    'bad_request': PercyBadRequest,
    'quota_exceeded': PercyQuotaExceeded,
}


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
        self._handle_response_errors(response)
        return response.json()

    def post(self, path, data, options={}):
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Authorization': self._token_header(),
        }
        response = requests.post(path, json=data, headers=headers)
        self._handle_response_errors(response)
        return response.json()

    def _handle_response_errors(self, response):
        if response.status_code >= 300:
            content = 'Unexpected HTTP status code {}: {}'.format(response.status_code, response.content)
            try:
                content = response.json()
            except Exception:
                error_status = None
            else:
                error_status = content['errors'][0]['status']
            exc = error_map.get(error_status, Error)
            raise exc(content)
