import os
import percy
import pytest
import sys

class BaseTestPercyEnvironment(object):
    def setup_method(self, method):
        self.original_env = {}
        self.original_env['TRAVIS_BUILD_ID'] = os.getenv('TRAVIS_BUILD_ID', None)
        self.original_env['TRAVIS_BUILD_NUMBER'] = os.getenv('TRAVIS_BUILD_NUMBER', None)
        self.original_env['TRAVIS_COMMIT'] = os.getenv('TRAVIS_COMMIT', None)
        self.original_env['TRAVIS_BRANCH'] = os.getenv('TRAVIS_BRANCH', None)
        self.original_env['TRAVIS_PULL_REQUEST'] = os.getenv('TRAVIS_PULL_REQUEST', None)
        self.original_env['TRAVIS_PULL_REQUEST_BRANCH'] = os.getenv('TRAVIS_PULL_REQUEST_BRANCH', None)

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
            'PERCY_TARGET_BRANCH',
            'PERCY_TARGET_COMMIT',
            'PERCY_PULL_REQUEST',
            'PERCY_PARALLEL_NONCE',
            'PERCY_PARALLEL_TOTAL',

            # Unset Travis vars.
            'TRAVIS_BUILD_ID',
            'TRAVIS_BUILD_NUMBER',
            'TRAVIS_COMMIT',
            'TRAVIS_BRANCH',
            'TRAVIS_PULL_REQUEST',
            'TRAVIS_PULL_REQUEST_BRANCH',
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
            'CIRCLE_BUILD_NUM',
            'CIRCLE_WORKFLOW_WORKSPACE_ID',
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


            # Unset GitLab vars
            'GITLAB_CI',
            'CI_COMMIT_SHA',
            'CI_COMMIT_REF_NAME',
            'CI_JOB_ID',
            'CI_JOB_STAGE',
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

    def test_target_branch(self):
        assert self.environment.target_branch == None
        # Can be overridden with PERCY_TARGET_BRANCH.
        os.environ['PERCY_TARGET_BRANCH'] = 'staging'
        assert self.environment.target_branch == 'staging'

    def test_target_commit_sha(self):
        assert self.environment.target_commit_sha == None
        # Can be overridden with PERCY_TARGET_COMMIT.
        os.environ['PERCY_TARGET_COMMIT'] = 'test-target-commit'
        assert self.environment.target_commit_sha == 'test-target-commit'

    def test_pull_request_number(self):
        assert self.environment.pull_request_number == None
        # Can be overridden with PERCY_PULL_REQUEST.
        os.environ['PERCY_PULL_REQUEST'] = '1234'
        assert self.environment.pull_request_number == '1234'

    def test_commit_live(self, monkeypatch):
        def isstr(s):
            if sys.version_info >= (3,0):
                return isinstance(s, str)
            else:
                return isinstance(s, basestring)

        # Call commit using the real _raw_commit_data, which calls git underneath, so allow full
        # commit object with attributes containing any string. (Real data changes with each commit)
        commit_data = self.environment.commit_data
        assert isstr(commit_data['branch'])
        assert isstr(commit_data['sha'])
        assert isstr(commit_data['message'])
        assert isstr(commit_data['committed_at'])
        assert isstr(commit_data['author_name'])
        assert isstr(commit_data['author_email'])
        assert isstr(commit_data['committer_name'])
        assert isstr(commit_data['committer_email'])

    @pytest.fixture()
    def test_commit_with_failed_raw_commit(self, monkeypatch):
        # Call commit using faking a _raw_commit_data failure.
        # If git command fails, only data from environment variables.
        os.environ['PERCY_COMMIT'] = 'testcommitsha'
        os.environ['PERCY_BRANCH'] = 'testbranch'
        monkeypatch.setattr(self.environment, '_raw_commit_output', lambda x: '')
        assert self.environment.commit_data == {
            'branch': 'testbranch',
            'author_email': None,
            'author_name': None,
            'committer_email': None,
            'committer_name': None,
            'sha': 'testcommitsha',
        }
        self.clear_env_vars()

    @pytest.fixture()
    def test_commit_with_mocked_raw_commit(self, monkeypatch):
        # Call commit with _raw_commit_data returning mock data, so we can confirm it
        # gets formatted correctly
        os.environ['PERCY_BRANCH'] = 'the-coolest-branch'
        def fake_raw_commit(commit_sha):
            return """COMMIT_SHA:2fcd1b107aa25e62a06de7782d0c17544c669d139
                      AUTHOR_NAME:Tim Haines
                      AUTHOR_EMAIL:timhaines@example.com
                      COMMITTER_NAME:Other Tim Haines
                      COMMITTER_EMAIL:othertimhaines@example.com
                      COMMITTED_DATE:2018-03-10 14:41:02 -0800
                      COMMIT_MESSAGE:This is a great commit"""

        monkeypatch.setattr(self.environment, '_raw_commit_output', fake_raw_commit)
        assert self.environment.commit_data == {
            'branch': 'the-coolest-branch',
            'sha': '2fcd1b107aa25e62a06de7782d0c17544c669d139',
            'committed_at': '2018-03-10 14:41:02 -0800',
            'message': 'This is a great commit',
            'author_name': 'Tim Haines',
            'author_email': 'timhaines@example.com',
            'committer_name': 'Other Tim Haines',
            'committer_email': 'othertimhaines@example.com'
        }


    @pytest.fixture()
    def test_branch(self, monkeypatch):
        # Default calls _raw_branch_output and call git underneath, so allow any non-empty string.
        assert len(self.environment.branch) > 0

        # If git command fails, falls back to None and prints warning.
        monkeypatch.setattr(self.environment, '_raw_branch_output', lambda: '')
        assert self.environment.branch == None

        # Can be overridden with PERCY_BRANCH.
        os.environ['PERCY_BRANCH'] = 'foo'
        assert self.environment.branch == 'foo'

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
        os.environ['TRAVIS_PULL_REQUEST'] = 'false'
        os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = 'false'
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
        assert self.environment.branch == 'travis-pr-branch'

        os.environ['PERCY_BRANCH'] = 'foo'
        assert self.environment.branch == 'foo'

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'travis-commit-sha'

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
        os.environ['CIRCLE_BUILD_NUM'] = 'circle-build-number'
        os.environ['CIRCLE_WORKFLOW_WORKSPACE_ID'] = 'circle-workflow-workspace-id'
        os.environ['CIRCLE_NODE_TOTAL'] = '3'
        os.environ['CI_PULL_REQUESTS'] = 'https://github.com/owner/repo-name/pull/123'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'circle'

    def test_branch(self):
        assert self.environment.branch == 'circle-branch'

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'circle-commit-sha'

    def test_parallel_nonce(self):
        assert self.environment.parallel_nonce == 'circle-workflow-workspace-id'
        del os.environ['CIRCLE_WORKFLOW_WORKSPACE_ID']
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
        os.environ['SEMAPHORE_BRANCH_ID'] = 'semaphore-branch-id'
        os.environ['SEMAPHORE_BUILD_NUMBER'] = 'semaphore-build-number'
        os.environ['SEMAPHORE_THREAD_COUNT'] = '2'
        os.environ['PULL_REQUEST_NUMBER'] = '123'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'semaphore'

    def test_branch(self):
        assert self.environment.branch == 'semaphore-branch'

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


class TestGitlabEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestGitlabEnvironment, self).setup_method(self)
        os.environ['GITLAB_CI'] = 'true'
        os.environ['CI_COMMIT_SHA'] = 'gitlab-commit-sha'
        os.environ['CI_COMMIT_REF_NAME'] = 'gitlab-branch'
        os.environ['CI_JOB_ID'] = 'gitlab-job-id'
        os.environ['CI_JOB_STAGE'] = 'test'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'gitlab'

    def test_branch(self):
        assert self.environment.branch == 'gitlab-branch'

    def test_commit_sha(self):
        assert self.environment.commit_sha == 'gitlab-commit-sha'

    def test_parallel_nonce(self):
        assert self.environment.parallel_nonce == 'gitlab-branch/gitlab-job-id'
