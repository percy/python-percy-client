import os
import percy


class BaseTestPercyEnvironment(object):
    def setup_method(self, method):
        self.original_env = {}
        self.original_env['TRAVIS_BUILD_ID'] = os.getenv('TRAVIS_BUILD_ID', None)
        self.original_env['TRAVIS_BUILD_NUMBER'] = os.getenv('TRAVIS_BUILD_NUMBER', None)
        self.original_env['TRAVIS_COMMIT'] = os.getenv('TRAVIS_COMMIT', None)
        self.original_env['TRAVIS_BRANCH'] = os.getenv('TRAVIS_BRANCH', None)
        self.original_env['TRAVIS_PULL_REQUEST'] = os.getenv('TRAVIS_PULL_REQUEST', None)
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
            'PERCY_PARALLEL_NONCE',
            'PERCY_PARALLEL_TOTAL',

            # Unset Travis vars.
            'TRAVIS_BUILD_ID',
            'TRAVIS_BUILD_NUMBER',
            'TRAVIS_COMMIT',
            'TRAVIS_BRANCH',
            'TRAVIS_PULL_REQUEST',
            'TRAVIS_REPO_SLUG',
            'CI_NODE_TOTAL',

            # Unset Jenkins vars.
            'JENKINS_URL',
            'ghprbPullId',
            'ghprbActualCommit',
            'ghprbTargetBranch',

            # Unset Circle CI vars.
            'CIRCLECI',
            'CIRCLE_SHA1',
            'CIRCLE_BRANCH',
            'CIRCLE_PROJECT_USERNAME',
            'CIRCLE_PROJECT_REPONAME',
            'CIRCLE_BUILD_NUM',
            'CI_PULL_REQUESTS',

            # Unset Codeship vars.
            'CI_NAME',
            'CI_BRANCH',
            'CI_PULL_REQUEST',
            'CI_COMMIT_ID',
            'CI_BUILD_NUMBER',

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
            'SEMAPHORE_BUILD_NUMBER',
            'SEMAPHORE_CURRENT_THREAD',
            'PULL_REQUEST_NUMBER',
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

    def test_branch(self):
        assert self.environment.branch == 'master'
        # Can be overridden with PERCY_BRANCH.
        os.environ['PERCY_BRANCH'] = 'foo'
        assert self.environment.branch == 'foo'


class TestTravisEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestTravisEnvironment, self).setup_method(self)
        os.environ['TRAVIS_BUILD_ID'] = '1234'
        os.environ['TRAVIS_BUILD_NUMBER'] = 'build-number'
        os.environ['TRAVIS_PULL_REQUEST'] = '256'
        os.environ['TRAVIS_REPO_SLUG'] = 'travis/repo-slug'
        os.environ['TRAVIS_COMMIT'] = 'travis-commit-sha'
        os.environ['TRAVIS_BRANCH'] = 'travis-branch'
        os.environ['CI_NODE_TOTAL'] = '3'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'travis'

    def test_pull_request_number(self):
        assert self.environment.pull_request_number == '256'

        # PERCY env vars should take precendence over CI. Checked here once, assume other envs work.
        os.environ['PERCY_PULL_REQUEST'] = '1234'
        assert self.environment.pull_request_number == '1234'

    def test_branch(self):
        assert self.environment.branch == 'travis-branch'

        # PERCY env vars should take precendence over CI. Checked here once, assume other envs work.
        os.environ['PERCY_BRANCH'] = 'foo'
        assert self.environment.branch == 'foo'


class TestJenkinsEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestJenkinsEnvironment, self).setup_method(self)
        os.environ['JENKINS_URL'] = 'http://localhost:8080/'
        os.environ['ghprbPullId'] = '123'
        os.environ['ghprbTargetBranch'] = 'jenkins-target-branch'
        os.environ['ghprbActualCommit'] = 'jenkins-actual-commit'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'jenkins'


class TestCircleEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestCircleEnvironment, self).setup_method(self)
        os.environ['CIRCLECI'] = 'true'
        os.environ['CIRCLE_BRANCH'] = 'circle-branch'
        os.environ['CIRCLE_SHA1'] = 'circle-commit-sha'
        os.environ['CIRCLE_PROJECT_USERNAME'] = 'circle'
        os.environ['CIRCLE_PROJECT_REPONAME'] = 'repo-name'
        os.environ['CIRCLE_BUILD_NUM'] = 'build-number'
        os.environ['CIRCLE_NODE_TOTAL'] = '2'
        os.environ['CI_PULL_REQUESTS'] = 'https://github.com/owner/repo-name/pull/123'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'circle'

    def test_branch(self):
        assert self.environment.branch == 'circle-branch'


class TestCodeshipEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestCodeshipEnvironment, self).setup_method(self)
        os.environ['CI_NAME'] = 'codeship'
        os.environ['CI_BRANCH'] = 'codeship-branch'
        os.environ['CI_BUILD_NUMBER'] = 'codeship-build-number'
        os.environ['CI_PULL_REQUEST'] = 'false'  # This is always false on Codeship, unfortunately.
        os.environ['CI_COMMIT_ID'] = 'codeship-commit-sha'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'codeship'

    def test_branch(self):
        assert self.environment.branch == 'codeship-branch'


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


class TestSemaphoreEnvironment(BaseTestPercyEnvironment):
    def setup_method(self, method):
        super(TestSemaphoreEnvironment, self).setup_method(self)
        os.environ['SEMAPHORE'] = 'true'
        os.environ['BRANCH_NAME'] = 'semaphore-branch'
        os.environ['REVISION'] = 'semaphore-commit-sha'
        os.environ['SEMAPHORE_REPO_SLUG'] = 'repo-owner/repo-name'
        os.environ['SEMAPHORE_BUILD_NUMBER'] = 'semaphore-build-number'
        os.environ['SEMAPHORE_THREAD_COUNT'] = '2'
        os.environ['PULL_REQUEST_NUMBER'] = '123'
        self.environment = percy.Environment()

    def test_current_ci(self):
        assert self.environment.current_ci == 'semaphore'

    def test_branch(self):
        assert self.environment.branch == 'semaphore-branch'