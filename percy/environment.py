import os
import re
import subprocess

from percy import errors
from percy import utils

__all__ = ['Environment']

GIT_COMMIT_FORMAT = '%n'.join([
  'COMMIT_SHA:%H',
  'AUTHOR_NAME:%an',
  'AUTHOR_EMAIL:%ae',
  'COMMITTER_NAME:%cn',
  'COMMITTER_EMAIL:%ce',
  'COMMITTED_DATE:%ai',
  # Note: order is important, this must come last because the regex is a multiline match.
  'COMMIT_MESSAGE:%B',
]); # git show format uses %n for newlines.


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
        elif os.getenv('GITLAB_CI') == 'true':
            self._real_env = GitlabEnvironment()

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

    @property
    def target_branch(self):
        if os.getenv('PERCY_TARGET_BRANCH'):
            return os.getenv('PERCY_TARGET_BRANCH')
        return None

    @property
    def commit_data(self):

        # Try getting data from git
        # If this has a result, it means git is present in the system.
        raw_git_output = self._git_commit_output()

        # If not running in a git repo, allow undefined for certain commit attributes.
        def parse(regex):
            if not raw_git_output:
                return None
            match = regex.search(raw_git_output)
            if match:
                return match.group(1)
            else:
                return None

        return {
            # The only required attribute:
            'branch': self.branch,
            # An optional but important attribute:
            'sha': self.commit_sha or parse(re.compile("COMMIT_SHA:(.*)")),

            # Optional attributes:
            # If we have the git information, read from those rather than env vars.
            # The GIT_ environment vars are from the Jenkins Git Plugin, but could be
            # used generically. This behavior may change in the future.
            'message': parse(re.compile("COMMIT_MESSAGE:(.*)", flags=re.MULTILINE)),
            'committed_at': parse(re.compile("COMMITTED_DATE:(.*)")),
            'author_name': parse(re.compile("AUTHOR_NAME:(.*)")) or os.getenv('GIT_AUTHOR_NAME'),
            'author_email': parse(re.compile("AUTHOR_EMAIL:(.*)")) or os.getenv('GIT_AUTHOR_EMAIL'),
            'committer_name': parse(re.compile("COMMITTER_NAME:(.*)")) or os.getenv('GIT_COMMITTER_NAME'),
            'committer_email': parse(re.compile("COMMITTER_EMAIL:(.*)")) or os.getenv('GIT_COMMITTER_EMAIL'),
        }

    @property
    def commit_sha(self):
        # First, percy env var.
        if os.getenv('PERCY_COMMIT'):
            return os.getenv('PERCY_COMMIT')
        # Second, from the CI environment.
        if self._real_env and hasattr(self._real_env, 'commit_sha'):
            return self._real_env.commit_sha

    @property
    def target_commit_sha(self):
        if os.getenv('PERCY_TARGET_COMMIT'):
            return os.getenv('PERCY_TARGET_COMMIT')
        return None

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

    def _raw_git_output(self, args):
        process = subprocess.Popen(
            ['git'] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        return process.stdout.read().strip().decode('utf-8')

    def _raw_commit_output(self, commit_sha):
        # Make sure commit_sha is only alphanumeric characters to prevent command injection.
        if not commit_sha or len(commit_sha) > 100 or not commit_sha.isalnum():
            return ''

        args = ['show', commit_sha, '--quiet', '--format="' + GIT_COMMIT_FORMAT + '"'];
        return self._raw_git_output(args)

    def _git_commit_output(self):
        raw_git_output = ''
        # Try getting commit data from commit_sha set by environment variables
        if self.commit_sha:
          raw_git_output = self._raw_commit_output(self.commit_sha)

        # If there's no raw_git_output, it probably means there's not a sha, so try `HEAD`
        if not raw_git_output:
          raw_git_output = self._raw_commit_output('HEAD')

        return raw_git_output

    def _raw_branch_output(self):
        return self._raw_git_output(['rev-parse', '--abbrev-ref', 'HEAD'])

    def _get_origin_url(self):
        process = subprocess.Popen(
            'git config --get remote.origin.url', stdout=subprocess.PIPE, shell=True)
        return process.stdout.read().strip().decode('utf-8')



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
    def commit_sha(self):
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
    def commit_sha(self):
        return os.getenv('CIRCLE_SHA1')

    @property
    def parallel_nonce(self):
        return os.getenv('CIRCLE_WORKFLOW_WORKSPACE_ID') or os.getenv('CIRCLE_BUILD_NUM')

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


class GitlabEnvironment(object):
    @property
    def current_ci(self):
        return 'gitlab'

    @property
    def pull_request_number(self):
        return os.getenv('PERCY_PULL_REQUEST')

    @property
    def branch(self):
        return os.getenv('CI_COMMIT_REF_NAME')

    @property
    def commit_sha(self):
        return os.getenv('CI_COMMIT_SHA')

    @property
    def parallel_nonce(self):
        return '%s/%s' % (
            os.getenv('CI_COMMIT_REF_NAME'),
            os.getenv('CI_JOB_ID')
        )
