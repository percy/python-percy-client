import hashlib
from percy import utils

__all__ = ['Resource']


class Resource(object):

    def __init__(self, resource_url, is_root=False, **kwargs):
        self.resource_url = resource_url
        if 'sha' in kwargs and 'content' in kwargs or not ('sha' in kwargs or 'content' in kwargs):
            raise ValueError('Exactly one of sha or content is required.')
        self.content = kwargs.get('content')
        self.sha = kwargs.get('sha', utils.sha256hash(self.content))
        self.is_root = is_root
        self.mimetype = kwargs.get('mimetype')

    def serialize(self):
        return {
            'type': 'resources',
            'id': self.sha,
            'attributes': {
                'resource-url': self.resource_url,
                'mimetype': self.mimetype,
                'is-root': self.is_root,
            }
        }
