from percy import Resource
import os

__all__ = ['ResourceLoader']


class ResourceLoader(object):

    def __init__(self, root_dir=None, base_url=None):
        self.root_dir = root_dir
        self.base_url = base_url
        if self.base_url and self.base_url.endswith(os.path.sep):
            self.base_url = self.base_url[:-1]

    def build_resources(self):
        resources = []
        for root, dirs, files in os.walk(self.root_dir, followlinks=True):
            for file_name in files:
                path = os.path.join(root, file_name)
                with open(path, 'r+') as f:
                    content = f.read()
                    path_for_url = path.replace(self.root_dir, '', 1)

                    resource_url = "{0}{1}".format(self.base_url, path_for_url)
                    resources.append(Resource(resource_url=resource_url, content=content))
        return resources

    def snapshot_resources(self):
        pass
