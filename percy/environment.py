import os

def get_current_ci():
    if os.getenv('TRAVIS_BUILD_ID'):
        return 'travis'
    elif os.getenv('JENKINS_URL') and os.getenv('ghprbPullId'):  # Pull Request Builder plugin.
        return 'jenkins'
    elif os.getenv('CIRCLECI'):
        return 'circle'
    elif os.getenv('CI_NAME') == 'codeship':
        return 'codeship'
    elif os.getenv('DRONE') == 'true':
        return 'drone'
    elif os.getenv('SEMAPHORE') == 'true':
        return 'semaphore'
