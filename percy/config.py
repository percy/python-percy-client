import os
from percy import errors

__all__ = ['Config']


class Config(object):

    def __init__(self, api_url=None, default_widths=None, access_token=None):
        self._api_url = os.getenv('PERCY_API', api_url or 'https://percy.io/api/v1')
        self._default_widths = default_widths or []
        self._access_token = os.getenv('PERCY_TOKEN', access_token)

    @property
    def api_url(self):
        return self._api_url

    @api_url.setter
    def api_url(self, value):
        self._api_url = value

    @property
    def default_widths(self):
        return self._default_widths

    @default_widths.setter
    def default_widths(self, value):
        self._default_widths = value

    @property
    def access_token(self):
        if not self._access_token:
            raise errors.AuthError('You must set PERCY_TOKEN to authenticate.')
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value
