import os


class Config(object):

    @property
    def api_url(self):
        return 'https://percy.io/api/v1'

    @property
    def access_token(self):
        return os.getenv('PERCY_TOKEN')
