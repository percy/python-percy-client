import unittest
from percy import client


class TestPercyClient(unittest.TestCase):

    def setUp(self):
        self.percy_client = client.Client()

    def test_default_connection(self):
        self.assertNotEqual(self.percy_client.get_connection(), None)

    def test_create_build(self):
        pass
