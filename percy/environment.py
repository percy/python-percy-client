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
        # Fourth, fallback to 'master'.
        # STDERR.puts '[percy] Warning: not in a git repo, setting PERCY_BRANCH to "master".'
        return 'master'

    def _raw_branch_output(self):
        # TODO: `git rev-parse --abbrev-ref HEAD 2> /dev/null`.strip
        return

    @property
    def repo(self):
        if os.getenv('PERCY_REPO_SLUG'):
            return os.getenv('PERCY_REPO_SLUG')
        if self._real_env and hasattr(self._real_env, 'repo'):
            return self._real_env.repo

        raise NotImplementedError('needs PERCY_REPO_SLUG environment var')
        # TODO:
        # origin_url = _get_origin_url.strip
        # if origin_url == ''
        #   raise Percy::Client::Environment::RepoNotFoundError.new(
        #     'No local git repository found. ' +
        #     'You can manually set PERCY_REPO_SLUG to fix this.')
        # end
        # match = origin_url.match(Regexp.new('[:/]([^/]+\/[^/]+?)(\.git)?\Z'))
        # if !match
        #   raise Percy::Client::Environment::RepoNotFoundError.new(
        #     "Could not determine repository name from URL: #{origin_url.inspect}\n" +
        #     "You can manually set PERCY_REPO_SLUG to fix this.")
        # end
        # match[1]


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
      return os.getenv('TRAVIS_BRANCH')

    @property
    def repo(self):
      return os.getenv('TRAVIS_REPO_SLUG')


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
      return os.getenv('ghprbTargetBranch')


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

