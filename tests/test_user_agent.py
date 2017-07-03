import unittest
import re
import percy
from percy.user_agent import UserAgent

class TestPercyUserAgent(unittest.TestCase):
    def setUp(self):
        self.percy_client = percy.Client(config=percy.Config())

    def test_string(self):
        self.assertTrue(
            re.match(
                'Percy/v1 python-percy-client/[.\d]+ \(python/[.\d]+(; buildkite)?\)',
                str(UserAgent(self.percy_client))
            )
        )
