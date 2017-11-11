import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from percy.user_agent import UserAgent
from percy import utils

class Connection(object):
    def __init__(self, config, environment):
        self.config = config
        self.user_agent = str(UserAgent(config, environment))

    def _requests_retry_session(
        self,
        retries=3,
        backoff_factor=0.3,
        method_whitelist=['HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'],
        status_forcelist=(500, 502, 503, 504, 520, 524),
        session=None,
    ):
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            status=retries,
            method_whitelist=method_whitelist,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _token_header(self):
        return "Token token={0}".format(self.config.access_token)

    def get(self, path, options={}):
        headers = {
            'Authorization': self._token_header(),
            'User-Agent': self.user_agent,
        }
        response = self._requests_retry_session().get(path, headers=headers)
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
        response = self._requests_retry_session().post(path, json=data, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            utils.print_error('Received a {} error posting to: {}.'.format(response.status_code, path))
            utils.print_error(response.content)
            raise e
        return response.json()
