import unittest
import re
import percy
from percy.user_agent import UserAgent

class TestPercyUserAgent(unittest.TestCase):
    def setUp(self):
        percy_client = percy.Client(config=percy.Config())
        self.user_agent = UserAgent(percy_client)

    def test_string(self):
        self.assertTrue(
            re.match(
                'Percy/v1 python-percy-client/[.\d]+ \(python/[.\d]+; buildkite\)',
                str(self.user_agent)
            )
        )
