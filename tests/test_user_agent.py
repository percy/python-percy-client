import unittest
import re
import percy
from percy.user_agent import UserAgent

class TestPercyUserAgent(unittest.TestCase):
    def setUp(self):
        self.config = percy.Config(access_token='foo')
        self.environment = percy.Environment()

    def test_string(self):
        self.assertTrue(
            re.match(
                '^Percy/v1 python-percy-client/[.\d]+ \(python/[.\d]+(; travis)?\)$',
                str(UserAgent(self.config, self.environment))
            )
        )
