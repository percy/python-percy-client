import requests
# from IPython import embed
import re

class Connection(object):
    def __init__(self, config, environment):
        self.config = config
        self.environment = environment

    def _token_header(self):
        return "Token token={0}".format(self.config.access_token)

    def get(self, path, options={}):
        headers = {
            'Authorization': self._token_header(),
            'User-Agent': self._user_agent(),
        }
        response = requests.get(path, headers=headers)
        return response.json()

    def post(self, path, data, options={}):
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Authorization': self._token_header(),
            'User-Agent': self._user_agent(),
        }
        response = requests.post(path, json=data, headers=headers)
        # TODO(fotinakis): exception handling.
        # response.raise_for_status()
        return response.json()

    def _user_agent(self):
        client = ' '.join(filter(None, [
          "Percy/%s" % self._api_version(),
          "python-percy-client/%s" % self._client_version(),
        ]))

        environment = '; '.join(filter(None, [
          self._environment_info(),
          "python/%s" % (self._python_version()),
          self.environment.current_ci, # maybe
        ]))

        return "%s (%s)" % (client, environment)

    def _client_version(self):
        import percy
        return percy.__version__

    def _python_version(self):
        from platform import python_version
        return python_version()

    def _django_version(self):
        import django
        return django.get_version()

    def _api_version(self):
        return re.search('\w+$', self.config.api_url).group(0)

    def _environment_info(self):
        # we only detect django right now others could be added
        return "django/%s" % self._django_version()
