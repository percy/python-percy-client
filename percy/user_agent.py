import re
import percy

class UserAgent(object):

    def __init__(self, config, environment):
      self.config = config
      self.environment = environment

    def __str__(self):
        client = ' '.join(filter(None, [
          "Percy/%s" % self._api_version(),
          "python-percy-client/%s" % self._client_version(),
        ]))

        environment = '; '.join(filter(None, [
          self._environment_info(),
          "python/%s" % self._python_version(),
          self.environment.current_ci,
        ]))

        return "%s (%s)" % (client, environment)

    def _client_version(self):
        return percy.__version__

    def _python_version(self):
        try:
            from platform import python_version
            return python_version()
        except ImportError:
            return 'unknown'

    def _django_version(self):
        try:
            import django
            return "django/%s" % django.get_version()
        except ImportError:
            return None

    def _api_version(self):
        return re.search(r'\w+$', self.config.api_url).group(0)

    def _environment_info(self):
        # we only detect django right now others could be added
        return self._django_version()
