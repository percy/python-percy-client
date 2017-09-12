import os
import percy
try:
    # Python 3's pathname2url
    from urllib.request import pathname2url
except ImportError:
    # Python 2's pathname2url
    from urllib import pathname2url

from percy import utils

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

__all__ = ['ResourceLoader']

MAX_FILESIZE_BYTES = 15 * 1024**2  # 15 MiB.


class BaseResourceLoader(object):
    @property
    def build_resources(self):
        raise NotImplementedError('subclass must implement abstract method')

    @property
    def snapshot_resources(self):
        raise NotImplementedError('subclass must implement abstract method')


class ResourceLoader(BaseResourceLoader):
    def __init__(self, root_dir=None, base_url=None, webdriver=None):
        self.root_dir = root_dir
        self.base_url = base_url
        if self.base_url and self.base_url.endswith(os.path.sep):
            self.base_url = self.base_url[:-1]
        # TODO: more separate loader subclasses and pull out Selenium-specific logic?
        self.webdriver = webdriver

    @property
    def build_resources(self):
        resources = []
        if not self.root_dir:
            return resources
        for root, dirs, files in os.walk(self.root_dir, followlinks=True):
            for file_name in files:
                path = os.path.join(root, file_name)
                if os.path.getsize(path) > MAX_FILESIZE_BYTES:
                    continue
                with open(path, 'rb') as f:
                    content = f.read()

                    path_for_url = pathname2url(path.replace(self.root_dir, '', 1))
                    if self.base_url[-1] == '/' and path_for_url[0] == '/':
                        path_for_url = path_for_url.replace('/', '' , 1)


                    resource_url = "{0}{1}".format(self.base_url, path_for_url)
                    resource = percy.Resource(
                        resource_url=resource_url,
                        sha=utils.sha256hash(content),
                        local_path=os.path.abspath(path),
                    )
                    resources.append(resource)
        return resources

    @property
    def snapshot_resources(self):
        # Only one snapshot resource, the root page HTML.
        return [
            percy.Resource(
                # Assumes a Selenium webdriver interface.
                resource_url=urlparse(self.webdriver.current_url).path,
                is_root=True,
                mimetype='text/html',
                content=self.webdriver.page_source,
            )
        ]
