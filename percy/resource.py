import hashlib


class Resource(object):

    def __init__(self, resource_url, is_root=False, **kwargs):
        self.resource_url = resource_url
        if not (kwargs.get('sha') or kwargs.get('content')):
            raise ValueError('Either sha or content are required')
        self.sha = kwargs.get(
            'sha',
            hashlib.sha256(kwargs.get('content')).hexdigest()
        )
        self.content = kwargs.get('content')
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
