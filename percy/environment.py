import os
import re
import subprocess

from percy import errors
from percy import utils

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
        elif os.getenv('BUILDKITE') == 'true':
            self._real_env = BuildkiteEnvironment()

    @property
    def current_ci(self):
        if self._real_env:
            return self._real_env.current_ci

    @property
    def pull_request_number(self):
        if os.getenv('PERCY_PULL_REQUEST'):
            return os.getenv('PERCY_PULL_REQUEST')
        if self._real_env and hasattr(self._real_env, 'pull_request_number'):
            return self._real_env.pull_request_number

    @property
    def branch(self):
        # First, percy env var.
        if os.getenv('PERCY_BRANCH'):
            return os.getenv('PERCY_BRANCH')
        # Second, from the CI environment.
        if self._real_env and hasattr(self._real_env, 'branch'):
            return self._real_env.branch
        # Third, from the local git repo.
        raw_branch_output = self._raw_branch_output()
        if raw_branch_output:
            return raw_branch_output
        # Fourth, fallback to NONE.
        utils.print_error('[percy] Warning: unknown git repo, branch not detected.')
        return None

    def _raw_branch_output(self):
        if os.name == 'nt':
            process = subprocess.Popen(
                'git rev-parse --abbrev-ref HEAD 2> NUL', stdout=subprocess.PIPE, shell=True)
        else:
            process = subprocess.Popen(
                'git rev-parse --abbrev-ref HEAD 2> /dev/null', stdout=subprocess.PIPE, shell=True)
        return process.stdout.read().strip().decode('utf-8')

    def _get_origin_url(self):
        process = subprocess.Popen(
            'git config --get remote.origin.url', stdout=subprocess.PIPE, shell=True)
        return process.stdout.read().strip().decode('utf-8')

    @property
    def commit_sha(self):
        # First, percy env var.
        if os.getenv('PERCY_COMMIT'):
            return os.getenv('PERCY_COMMIT')
        # Second, from the CI environment.
        if self._real_env and hasattr(self._real_env, 'commit_sha'):
            return self._real_env.commit_sha

    @property
    def repo(self):
        if os.getenv('PERCY_REPO_SLUG') or os.getenv('PERCY_PROJECT'):
            return os.getenv('PERCY_REPO_SLUG') or os.getenv('PERCY_PROJECT')
        if self._real_env and hasattr(self._real_env, 'repo'):
            return self._real_env.repo

        origin_url = self._get_origin_url()
        if not origin_url:
          raise errors.RepoNotFoundError(
            'No local git repository found. ' +
            'You can manually set PERCY_PROJECT=org/repo-name to fix this.')

        match = re.compile(r'.*[:/]([^/]+\/[^/]+?)(\.git)?\Z').match(origin_url)
        if not match:
          raise errors.RepoNotFoundError(
            "Could not determine repository name from URL: {0}\n" +
            "You can manually set PERCY_PROJECT=org/repo-name to fix this.".format(origin_url))
        return match.group(1)

    @property
    def parallel_nonce(self):
        if os.getenv('PERCY_PARALLEL_NONCE'):
          return os.getenv('PERCY_PARALLEL_NONCE')
        if self._real_env and hasattr(self._real_env, 'parallel_nonce'):
            return self._real_env.parallel_nonce

    @property
    def parallel_total_shards(self):
        if os.getenv('PERCY_PARALLEL_TOTAL'):
            return int(os.getenv('PERCY_PARALLEL_TOTAL'))
        if self._real_env and hasattr(self._real_env, 'parallel_total_shards'):
            return self._real_env.parallel_total_shards


class TravisEnvironment(object):
    @property
    def current_ci(self):
        return 'travis'

    @property
    def pull_request_number(self):
        pr_num = os.getenv('TRAVIS_PULL_REQUEST')
        if pr_num != 'false':
            return pr_num

    @property
    def branch(self):
        if self.pull_request_number and os.getenv('TRAVIS_PULL_REQUEST_BRANCH'):
            return os.getenv('TRAVIS_PULL_REQUEST_BRANCH')
        return os.getenv('TRAVIS_BRANCH')

    @property
    def repo(self):
        return os.getenv('TRAVIS_REPO_SLUG')

    @property
    def commit_sha(self):
        if self.pull_request_number and os.getenv('TRAVIS_PULL_REQUEST_SHA'):
            return os.getenv('TRAVIS_PULL_REQUEST_SHA')
        return os.getenv('TRAVIS_COMMIT')

    @property
    def parallel_nonce(self):
        return os.getenv('TRAVIS_BUILD_NUMBER')

    @property
    def parallel_total_shards(self):
        if os.getenv('CI_NODE_TOTAL', '').isdigit():
            return int(os.getenv('CI_NODE_TOTAL'))


class JenkinsEnvironment(object):
    @property
    def current_ci(self):
        return 'jenkins'

    @property
    def pull_request_number(self):
        # GitHub Pull Request Builder plugin.
        return os.getenv('ghprbPullId')

    @property
    def branch(self):
        return os.getenv('ghprbSourceBranch')

    @property
    def commit_sha(self):
        return os.getenv('ghprbActualCommit') or os.getenv('GIT_COMMIT')

    @property
    def parallel_nonce(self):
        return os.getenv('BUILD_NUMBER')


class CircleEnvironment(object):
    @property
    def current_ci(self):
        return 'circle'

    @property
    def pull_request_number(self):
        pr_url = os.getenv('CI_PULL_REQUEST')
        if pr_url:
          return os.getenv('CI_PULL_REQUEST').split('/')[-1]

    @property
    def branch(self):
        return os.getenv('CIRCLE_BRANCH')

    @property
    def repo(self):
        return "{0}/{1}".format(
            os.getenv('CIRCLE_PROJECT_USERNAME'),
            os.getenv('CIRCLE_PROJECT_REPONAME'),
        )

    @property
    def commit_sha(self):
        return os.getenv('CIRCLE_SHA1')

    @property
    def parallel_nonce(self):
        return os.getenv('CIRCLE_BUILD_NUM')

    @property
    def parallel_total_shards(self):
        if os.getenv('CIRCLE_NODE_TOTAL', '').isdigit():
            return int(os.getenv('CIRCLE_NODE_TOTAL'))


class CodeshipEnvironment(object):
    @property
    def current_ci(self):
        return 'codeship'

    @property
    def pull_request_number(self):
        pr_num = os.getenv('CI_PULL_REQUEST')
        # Unfortunately, codeship seems to always returns 'false', so let this be null.
        if pr_num != 'false':
          return pr_num

    @property
    def branch(self):
        return os.getenv('CI_BRANCH')

    @property
    def commit_sha(self):
        return os.getenv('CI_COMMIT_ID')

    @property
    def parallel_nonce(self):
        return os.getenv('CI_BUILD_NUMBER')

    @property
    def parallel_total_shards(self):
        if os.getenv('CI_NODE_TOTAL', '').isdigit():
            return int(os.getenv('CI_NODE_TOTAL'))


class DroneEnvironment(object):
    @property
    def current_ci(self):
        return 'drone'

    @property
    def pull_request_number(self):
        return os.getenv('CI_PULL_REQUEST')

    @property
    def branch(self):
        return os.getenv('DRONE_BRANCH')

    @property
    def commit_sha(self):
        return os.getenv('DRONE_COMMIT')


class SemaphoreEnvironment(object):
    @property
    def current_ci(self):
        return 'semaphore'

    @property
    def pull_request_number(self):
        return os.getenv('PULL_REQUEST_NUMBER')

    @property
    def branch(self):
        return os.getenv('BRANCH_NAME')

    @property
    def repo(self):
      return os.getenv('SEMAPHORE_REPO_SLUG')

    @property
    def commit_sha(self):
        return os.getenv('REVISION')

    @property
    def parallel_nonce(self):
        return '%s/%s' % (
            os.getenv('SEMAPHORE_BRANCH_ID'),
            os.getenv('SEMAPHORE_BUILD_NUMBER')
        )

    @property
    def parallel_total_shards(self):
        if os.getenv('SEMAPHORE_THREAD_COUNT', '').isdigit():
            return int(os.getenv('SEMAPHORE_THREAD_COUNT'))


class BuildkiteEnvironment(object):
    @property
    def current_ci(self):
        return 'buildkite'

    @property
    def pull_request_number(self):
        return os.getenv('BUILDKITE_PULL_REQUEST')

    @property
    def branch(self):
        return os.getenv('BUILDKITE_BRANCH')

    @property
    def commit_sha(self):
        if os.getenv('BUILDKITE_COMMIT') == 'HEAD':
            # Buildkite mixes SHAs and non-SHAs in BUILDKITE_COMMIT, so we return null if non-SHA.
            return
        return os.getenv('BUILDKITE_COMMIT')

    @property
    def parallel_nonce(self):
        return os.getenv('BUILDKITE_BUILD_ID')

    @property
    def parallel_total_shards(self):
        if os.getenv('BUILDKITE_PARALLEL_JOB_COUNT', '').isdigit():
            return int(os.getenv('BUILDKITE_PARALLEL_JOB_COUNT'))
