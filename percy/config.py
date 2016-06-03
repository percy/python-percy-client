import os

class AuthError(Exception):
  pass

class Config(object):

    @property
    def api_url(self):
        return os.getenv('PERCY_API', 'https://percy.io/api/v1')

    @property
    def access_token(self):
        access_token = os.getenv('PERCY_TOKEN')
        if not access_token:
          raise AuthError('You must set PERCY_TOKEN to authenticate.')
        return access_token
