import os
import percy
import pytest


class BaseTestPercyEnvironment(object):
    def setup_method(self, method):
        self.original_env = {}
        self.original_env['TRAVIS_BUILD_ID'] = os.getenv('TRAVIS_BUILD_ID', None)
        self.original_env['TRAVIS_BUILD_NUMBER'] = os.getenv('TRAVIS_BUILD_NUMBER', None)
        self.original_env['TRAVIS_COMMIT'] = os.getenv('TRAVIS_COMMIT', None)
        self.original_env['TRAVIS_BRANCH'] = os.getenv('TRAVIS_BRANCH', None)
        self.original_env['TRAVIS_PULL_REQUEST'] = os.getenv('TRAVIS_PULL_REQUEST', None)
        self.original_env['TRAVIS_PULL_REQUEST_BRANCH'] = os.getenv('TRAVIS_PULL_REQUEST_BRANCH', None)
        self.original_env['TRAVIS_PULL_REQUEST_SHA'] = os.getenv('TRAVIS_PULL_REQUEST_SHA', None)
        self.original_env['TRAVIS_REPO_SLUG'] = os.getenv('TRAVIS_REPO_SLUG', None)

    def teardown_method(self, method):
        self.clear_env_vars()

        # Restore the original environment variables.
        for key, value in self.original_env.items():
            if value:
                os.environ[key] = value

    def clear_env_vars(self):
        all_possible_env_vars = [
            # Unset Percy vars.
            'PERCY_COMMIT',
            'PERCY_BRANCH',
            'PERCY_PULL_REQUEST',
            'PERCY_REPO_SLUG',
            'PERCY_PROJECT',
            'PERCY_PARALLEL_NONCE',
            'PERCY_PARALLEL_TOTAL',

            # Unset Travis vars.
            'TRAVIS_BUILD_ID',
            'TRAVIS_BUILD_NUMBER',
            'TRAVIS_COMMIT',
            'TRAVIS_BRANCH',
            'TRAVIS_PULL_REQUEST',
            'TRAVIS_PULL_REQUEST_BRANCH',
            'TRAVIS_PULL_REQUEST_SHA',
            'TRAVIS_REPO_SLUG',
            'CI_NODE_TOTAL',

            # Unset Jenkins vars.
            'JENKINS_URL',
            'BUILD_NUMBER',
            'ghprbPullId',
            'ghprbActualCommit',
            'ghprbSourceBranch',
            'GIT_COMMIT',

            # Unset Circle CI vars.
            'CIRCLECI',
            'CIRCLE_SHA1',
            'CIRCLE_BRANCH',
            'CIRCLE_PROJECT_USERNAME',
            'CIRCLE_PROJECT_REPONAME',
            'CIRCLE_BUILD_NUM',
            'CI_PULL_REQUESTS',
            'CIRCLE_NODE_TOTAL',

            # Unset Codeship vars.
            'CI_NAME',
            'CI_BRANCH',
            'CI_PULL_REQUEST',
            'CI_COMMIT_ID',
            'CI_BUILD_NUMBER',
            'CI_NODE_TOTAL',

            # Unset Drone vars.
            'CI',
            'DRONE',
            'DRONE_COMMIT',
            'DRONE_BRANCH',
            'CI_PULL_REQUEST',

            # Unset Semaphore CI vars
            'CI',
            'SEMAPHORE',
            'REVISION',
            'BRANCH_NAME',
            'SEMAPHORE_REPO_SLUG',
            'SEMAPHORE_BRANCH_ID',
            'SEMAPHORE_BUILD_NUMBER',
            'SEMAPHORE_CURRENT_THREAD',
            'SEMAPHORE_THREAD_COUNT',
            'PULL_REQUEST_NUMBER',

            # Unset Buildkite vars
            'BUILDKITE',
            'BUILDKITE_COMMIT',
            'BUILDKITE_BRANCH',
            'BUILDKITE_PULL_REQUEST',
            'BUILDKITE_BUILD_ID',
            'BUILDKITE_PARALLEL_JOB_COUNT',
        ]
        for env_var in all_possible_env_vars:
            if os.getenv(env_var):
                del os.environ[env_var]


class TestNoEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestNoEnvironment, self).setup_method(self)
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == None

    def test_pull_request_number(self):
        assert self.environment.pull_request_number == None
        # Can be overridden with PERCY_PULL_REQUEST.
        os.environ['PERCY_PULL_REQUEST'] = '1234'
        assert self.environment.pull_request_number == '1234'

    @pytest.fixture(autouse=True)
    def test_branch(self, monkeypatch):
        # Default calls _raw_branch_output and call git underneath, so allow any non-empty string.
        assert len(self.environment.branch) > 0

        # If git command fails, falls back to None and prints warning.
        monkeypatch.setattr(self.environment, '_raw_branch_output', lambda: '')
        assert self.environment.branch == None

        # Can be overridden with PERCY_BRANCH.
        os.environ['PERCY_BRANCH'] = 'foo'
        assert self.environment.branch == 'foo'

    def test_repo(self):
        assert self.environment.repo == 'percy/python-percy-client'  # This actual repo name.
        # Can be overridden with PERCY_PROJECT.
        os.environ['PERCY_PROJECT'] = 'foo/bar-qux'
        assert self.environment.repo == 'foo/bar-qux'
        # Deprecated: can be overridden with PERCY_REPO_SLUG.
        os.environ['PERCY_REPO_SLUG'] = 'foo/bar'
        assert self.environment.repo == 'foo/bar'

    def test_commit_sha(self):
        assert not self.environment.commit_sha
        # Can be overridden with PERCY_COMMIT.
        os.environ['PERCY_COMMIT'] = 'commit-sha'
        assert self.environment.commit_sha == 'commit-sha'

    def test_parallel_nonce(self):
        os.environ['PERCY_PARALLEL_NONCE'] = 'foo'
        assert self.environment.parallel_nonce == 'foo'

    def test_parallel_total(self):
        os.environ['PERCY_PARALLEL_TOTAL'] = '2'
        assert self.environment.parallel_total_shards == 2


class TestTravisEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestTravisEnvironment, self).setup_method(self)
        os.environ['TRAVIS_BUILD_ID'] = '1234'
        os.environ['TRAVIS_BUILD_NUMBER'] = 'travis-build-number'
        os.environ['TRAVIS_REPO_SLUG'] = 'travis/repo-slug'
        os.environ['TRAVIS_PULL_REQUEST'] = 'false'
        os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = 'false'
        os.environ['TRAVIS_PULL_REQUEST_SHA'] = 'false'
        os.environ['TRAVIS_COMMIT'] = 'travis-commit-sha'
        os.environ['TRAVIS_BRANCH'] = 'travis-branch'
        os.environ['CI_NODE_TOTAL'] = '3'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'travis'

    def test_pull_request_number(self):
        assert self.environment.pull_request_number == None

        os.environ['TRAVIS_PULL_REQUEST'] = '256'
        assert self.environment.pull_request_number == '256'

        # PERCY env vars should take precendence over CI. Checked here once, assume other envs work.
        os.environ['PERCY_PULL_REQUEST'] = '1234'
        assert self.environment.pull_request_number == '1234'

    def test_branch(self):
        assert self.environment.branch == 'travis-branch'

        # Triggers special path if PR build in Travis.
        os.environ['TRAVIS_PULL_REQUEST'] = '256'
        os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = 'travis-pr-branch'
        os.environ['TRAVIS_PULL_REQUEST_SHA'] = 'travis-pr-head-commit-sha'
        assert self.environment.branch == 'travis-pr-branch'

        os.environ['PERCY_BRANCH'] = 'foo'
        assert self.environment.branch == 'foo'

    def test_repo(self):
        assert self.environment.repo == 'travis/repo-slug'

        os.environ['PERCY_REPO_SLUG'] = 'foo'
        assert self.environment.repo == 'foo'

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'travis-commit-sha'

        # Triggers special path if PR build in Travis.
        os.environ['TRAVIS_PULL_REQUEST'] = '256'
        os.environ['TRAVIS_PULL_REQUEST_SHA'] = 'travis-pr-head-commit-sha'
        assert self.environment.commit_sha == 'travis-pr-head-commit-sha'

        os.environ['PERCY_COMMIT'] = 'commit-sha'
        assert self.environment.commit_sha == 'commit-sha'

    def test_parallel_nonce(self):
        assert self.environment.parallel_nonce == 'travis-build-number'

        os.environ['PERCY_PARALLEL_NONCE'] = 'nonce'
        assert self.environment.parallel_nonce == 'nonce'

    def test_parallel_total(self):
        assert self.environment.parallel_total_shards == 3

        os.environ['CI_NODE_TOTAL'] = ''
        assert self.environment.parallel_total_shards == None

        os.environ['PERCY_PARALLEL_TOTAL'] = '1'
        assert self.environment.parallel_total_shards == 1


class TestJenkinsEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestJenkinsEnvironment, self).setup_method(self)
        os.environ['JENKINS_URL'] = 'http://localhost:8080/'
        os.environ['BUILD_NUMBER'] = 'jenkins-build-number'
        os.environ['ghprbSourceBranch'] = 'jenkins-source-branch'
        os.environ['ghprbActualCommit'] = 'jenkins-commit-sha'
        os.environ['GIT_COMMIT'] = 'jenkins-commit-sha-from-git-plugin'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'jenkins'

    def test_pull_request_number(self):
        assert self.environment.pull_request_number == None

        os.environ['ghprbPullId'] = '256'
        assert self.environment.pull_request_number == '256'

    def test_branch(self):
        assert self.environment.branch == 'jenkins-source-branch'

    def test_repo(self):
        assert self.environment.repo == 'percy/python-percy-client'  # Fallback to default.

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'jenkins-commit-sha'
        del os.environ['ghprbActualCommit']
        assert self.environment.commit_sha == 'jenkins-commit-sha-from-git-plugin'

    def test_parallel_nonce(self):
        assert self.environment.parallel_nonce == 'jenkins-build-number'

    def test_parallel_total(self):
        assert self.environment.parallel_total_shards is None


class TestCircleEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestCircleEnvironment, self).setup_method(self)
        os.environ['CIRCLECI'] = 'true'
        os.environ['CIRCLE_BRANCH'] = 'circle-branch'
        os.environ['CIRCLE_SHA1'] = 'circle-commit-sha'
        os.environ['CIRCLE_PROJECT_USERNAME'] = 'circle'
        os.environ['CIRCLE_PROJECT_REPONAME'] = 'repo-name'
        os.environ['CIRCLE_BUILD_NUM'] = 'circle-build-number'
        os.environ['CIRCLE_NODE_TOTAL'] = '3'
        os.environ['CI_PULL_REQUESTS'] = 'https://github.com/owner/repo-name/pull/123'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'circle'

    def test_branch(self):
        assert self.environment.branch == 'circle-branch'

    def test_repo(self):
        assert self.environment.repo == 'circle/repo-name'

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'circle-commit-sha'

    def test_parallel_nonce(self):
        assert self.environment.parallel_nonce == 'circle-build-number'

    def test_parallel_total(self):
        assert self.environment.parallel_total_shards == 3


class TestCodeshipEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestCodeshipEnvironment, self).setup_method(self)
        os.environ['CI_NAME'] = 'codeship'
        os.environ['CI_BRANCH'] = 'codeship-branch'
        os.environ['CI_BUILD_NUMBER'] = 'codeship-build-number'
        os.environ['CI_PULL_REQUEST'] = 'false'  # This is always false on Codeship, unfortunately.
        os.environ['CI_COMMIT_ID'] = 'codeship-commit-sha'
        os.environ['CI_NODE_TOTAL'] = '3'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'codeship'

    def test_branch(self):
        assert self.environment.branch == 'codeship-branch'

    def test_repo(self):
        assert self.environment.repo == 'percy/python-percy-client'  # Fallback to default.

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'codeship-commit-sha'

    def test_parallel_nonce(self):
        assert self.environment.parallel_nonce == 'codeship-build-number'

    def test_parallel_total(self):
        assert self.environment.parallel_total_shards == 3


class TestDroneEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestDroneEnvironment, self).setup_method(self)
        os.environ['DRONE'] = 'true'
        os.environ['DRONE_COMMIT'] = 'drone-commit-sha'
        os.environ['DRONE_BRANCH'] = 'drone-branch'
        os.environ['CI_PULL_REQUEST'] = '123'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'drone'

    def test_branch(self):
        assert self.environment.branch == 'drone-branch'

    def test_repo(self):
        assert self.environment.repo == 'percy/python-percy-client'  # Fallback to default.

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'drone-commit-sha'

    def test_parallel_nonce(self):
        assert self.environment.parallel_nonce is None

    def test_parallel_total(self):
        assert self.environment.parallel_total_shards is None


class TestSemaphoreEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestSemaphoreEnvironment, self).setup_method(self)
        os.environ['SEMAPHORE'] = 'true'
        os.environ['BRANCH_NAME'] = 'semaphore-branch'
        os.environ['REVISION'] = 'semaphore-commit-sha'
        os.environ['SEMAPHORE_REPO_SLUG'] = 'semaphore/repo-name'
        os.environ['SEMAPHORE_BRANCH_ID'] = 'semaphore-branch-id'
        os.environ['SEMAPHORE_BUILD_NUMBER'] = 'semaphore-build-number'
        os.environ['SEMAPHORE_THREAD_COUNT'] = '2'
        os.environ['PULL_REQUEST_NUMBER'] = '123'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'semaphore'

    def test_branch(self):
        assert self.environment.branch == 'semaphore-branch'

    def test_repo(self):
        assert self.environment.repo == 'semaphore/repo-name'

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'semaphore-commit-sha'

    def test_parallel_nonce(self):
        expected_nonce = 'semaphore-branch-id/semaphore-build-number'
        assert self.environment.parallel_nonce == expected_nonce

    def test_parallel_total(self):
        assert self.environment.parallel_total_shards == 2


class TestBuildkiteEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestBuildkiteEnvironment, self).setup_method(self)
        os.environ['BUILDKITE'] = 'true'
        os.environ['BUILDKITE_COMMIT'] = 'buildkite-commit-sha'
        os.environ['BUILDKITE_BRANCH'] = 'buildkite-branch'
        os.environ['BUILDKITE_PULL_REQUEST'] = 'false'
        os.environ['BUILDKITE_BUILD_ID'] = 'buildkite-build-id'
        os.environ['BUILDKITE_PARALLEL_JOB_COUNT'] = '2'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'buildkite'

    def test_branch(self):
        assert self.environment.branch == 'buildkite-branch'

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'buildkite-commit-sha'
        os.environ['BUILDKITE_COMMIT'] = 'HEAD'
        assert self.environment.commit_sha is None


    def test_parallel_nonce(self):
        assert self.environment.parallel_nonce == 'buildkite-build-id'

    def test_parallel_total(self):
        assert self.environment.parallel_total_shards == 2
