from __future__ import print_function

import percy
from percy import errors

__all__ = ['Runner']


class Runner(object):

    def __init__(self, loader=None, config=None, client=None):
        self.loader = loader
        self.config = config or percy.Config()
        self.client = client or percy.Client(config=self.config)
        self._current_build = None

    def initialize_build(self, **kwargs):
        build_resources = []
        build_resources = self.loader.build_resources if self.loader else []
        sha_to_build_resource = {r.sha: r for r in build_resources}

        self._current_build = self.client.create_build(resources=build_resources, **kwargs)

        missing_resources = self._current_build['data']['relationships']['missing-resources']
        missing_resources = missing_resources.get('data', [])

        for missing_resource in missing_resources:
            sha = missing_resource['id']
            resource = sha_to_build_resource.get(sha)
            # This resource should always exist, but if by chance it doesn't we make it safe here.
            # A nicer error will be raised by the finalize API when the resource is still missing.
            if resource:
                print('Uploading new build resource: {}'.format(resource.resource_url))
                if resource.local_path:
                    with open(resource.local_path, 'r') as f:
                        content = f.read()
                else:
                    content = resource.content
                self.client.upload_resource(self._current_build['data']['id'], content)

    def snapshot(self, name):
        if not self._current_build:
            raise errors.UninitializedBuildError('Cannot call snapshot before build is initialized')

        # resources = [
        #     percy.Resource(
        #         resource_url='/',
        #         is_root=True,
        #         mimetype='text/html',
        #         content=self.browser.page_source,
        #     ),
        # ]
        # sha_to_resource = {r.sha: r for r in resources}
        # snapshot_data = self.client.create_snapshot(build_data['data']['id'], resources)

        # for missing_resource in snapshot_data['data']['relationships']['missing-resources']['data']:
        #     self.client.upload_resource(build_id, sha_to_resource[missing_resource['id']].content)

        # self.client.finalize_snapshot(snapshot_data['data']['id'])
        pass

    def finalize_build(self):
        # self.client.finalize_build(build_id)
        pass