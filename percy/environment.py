import os

__all__ = ['Environment']

class Environment(object):
    def __init__(self):
        self._real_env = None
        if os.getenv('TRAVIS_BUILD_ID'):
            self._real_env = TravisEnvironment()
        elif os.getenv('JENKINS_URL'):
            self._real_env = JenkinsEnvironment()
        elif os.getenv('CIRCLECI'):
            self._real_env = CircleEnvironment()
        elif os.getenv('CI_NAME') == 'codeship':
            self._real_env = CodeshipEnvironment()
        elif os.getenv('DRONE') == 'true':
            self._real_env = DroneEnvironment()
        elif os.getenv('SEMAPHORE') == 'true':
            self._real_env = SemaphoreEnvironment()

    @property
    def current_ci(self):
        if self._real_env:
            return self._real_env.current_ci

    @property
    def pull_request_number(self):
        if os.getenv('PERCY_PULL_REQUEST'):
            return os.getenv('PERCY_PULL_REQUEST')
        if self._real_env:
            return self._real_env.pull_request_number


class TravisEnvironment(object):
    @property
    def current_ci(self):
        return 'travis'

    @property
    def pull_request_number(self):
        pr_num = os.getenv('TRAVIS_PULL_REQUEST')
        if pr_num != 'false':
            return pr_num


class JenkinsEnvironment(object):
    @property
    def current_ci(self):
        return 'jenkins'

    @property
    def pull_request_number(self):
        # GitHub Pull Request Builder plugin.
        return os.getenv('ghprbPullId')


class CircleEnvironment(object):
    @property
    def current_ci(self):
        return 'circle'

    @property
    def pull_request_number(self):
        pr_url = os.getenv('CI_PULL_REQUEST')
        if pr_url:
          return os.getenv('CI_PULL_REQUEST').split('/')[-1]


class CodeshipEnvironment(object):
    @property
    def current_ci(self):
        return 'codeship'

    @property
    def pull_request_number(self):
        # Unfortunately, codeship seems to always returns 'false' for CI_PULL_REQUEST. For now, return null.
        pr_num = os.getenv('CI_PULL_REQUEST')
        if pr_num != 'false':
          return pr_num


class DroneEnvironment(object):
    @property
    def current_ci(self):
        return 'drone'

    @property
    def pull_request_number(self):
        return os.getenv('CI_PULL_REQUEST')


class SemaphoreEnvironment(object):
    @property
    def current_ci(self):
        return 'semaphore'

    @property
    def pull_request_number(self):
        return os.getenv('PULL_REQUEST_NUMBER')


