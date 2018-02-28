from __future__ import print_function

import os
import percy
from percy import errors
from percy import utils

__all__ = ['Runner']


class Runner(object):

    def __init__(self, loader=None, config=None, client=None):
        self.loader = loader
        self.config = config or percy.Config()
        self.client = client or percy.Client(config=self.config)
        self._current_build = None

        self._is_enabled = os.getenv('PERCY_ENABLE', '1') == '1'

        # Sanity check environment and auth setup. If in CI and Percy is disabled, print an error.
        if self._is_enabled:
            try:
                self.client.config.access_token
            except errors.AuthError:
                if self.client.environment.current_ci:
                    utils.print_error('[percy] Warning: Percy is disabled, no PERCY_TOKEN set.')
                self._is_enabled = False

    def initialize_build(self, **kwargs):
        # Silently pass if Percy is disabled.
        if not self._is_enabled:
            return

        build_resources = []
        build_resources = self.loader.build_resources if self.loader else []
        sha_to_build_resource = {}
        for build_resource in build_resources:
            sha_to_build_resource[build_resource.sha] = build_resource

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

                # Optimization: we don't hold all build resources in memory. Instead we store a
                # "local_path" variable that be used to read the file again if it is needed.
                if resource.local_path:
                    with open(resource.local_path, 'rb') as f:
                        content = f.read()
                else:
                    content = resource.content
                self.client.upload_resource(self._current_build['data']['id'], content)

    @property
    def build_id(self):
      if not self._is_enabled:
        return
      if not self._current_build:
        raise errors.UninitializedBuildError('Cannot get current build id before build is initialized')
      return self._current_build['data']['id']

    def snapshot(self, **kwargs):
        # Silently pass if Percy is disabled.
        if not self._is_enabled:
            return
        if not self._current_build:
            raise errors.UninitializedBuildError('Cannot call snapshot before build is initialized')

        root_resource = self.loader.snapshot_resources[0]
        build_id = self._current_build['data']['id']
        snapshot_data = self.client.create_snapshot(build_id, [root_resource], **kwargs)

        missing_resources = snapshot_data['data']['relationships']['missing-resources']
        missing_resources = missing_resources.get('data', [])

        if missing_resources:
            # There can only be one missing resource in this case, the root_resource.
            self.client.upload_resource(build_id, root_resource.content)

        self.client.finalize_snapshot(snapshot_data['data']['id'])

    def finalize_build(self):
        # Silently pass if Percy is disabled.
        if not self._is_enabled:
            return
        if not self._current_build:
            raise errors.UninitializedBuildError(
                'Cannot finalize_build before build is initialized.')
        self.client.finalize_build(self._current_build['data']['id'])
        self._current_build = None
