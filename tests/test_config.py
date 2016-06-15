import os
import unittest

from percy import errors
from percy import config


class TestPercyConfig(unittest.TestCase):
    def setUp(self):
        os.environ['PERCY_TOKEN'] = 'abcd1234'
        self.config = config.Config()

    def tearDown(self):
        del os.environ['PERCY_TOKEN']

    def test_getters(self):
        self.assertEqual(self.config.api_url, 'https://percy.io/api/v1')
        self.assertEqual(self.config.default_widths, [])
        self.assertEqual(self.config.access_token, 'abcd1234')

    def test_setters(self):
        self.config.api_url = 'https://microsoft.com/'
        self.assertEqual(self.config.api_url, 'https://microsoft.com/')

        self.assertEqual(self.config.default_widths, [])
        self.config.default_widths = (1280, 375)
        self.assertEqual(self.config.default_widths, (1280, 375))

        self.config.access_token = None
        self.assertRaises(errors.AuthError, lambda: self.config.access_token)

        self.config.access_token = 'percy123'
        self.assertEqual(self.config.access_token, 'percy123')
