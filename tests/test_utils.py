# -*- coding: utf-8 -*-

import os
import sys
import unittest

from percy import utils


class TestPercyUtils(unittest.TestCase):
    def test_sha256hash(self):
        self.assertEqual(
          utils.sha256hash('foo'),
          '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae',
        )
        self.assertEqual(
          utils.sha256hash(u'I ♡ Python'),
          '5ebc381ed49ffbbff4efabd2c5e2ac5f116984cd72fffa4272cc528176bb09f6',
        )

        if sys.version_info >= (3,0):
          binary_content = b'\x01\x02\x99'
        else:
          binary_content = '\x01\x02\x99'

        self.assertEqual(
          utils.sha256hash(binary_content),
          '17b9440d8fa6bb5eb0e06a68dd3882c01c5a757f889118f9fbdf50e6e7025581',
        )

    def test_base64encode(self):
        self.assertEqual(utils.base64encode('foo'), 'Zm9v')
        self.assertEqual(utils.base64encode(u'I ♡ Python'), 'SSDimaEgUHl0aG9u')

        if sys.version_info >= (3,0):
          binary_content = b'\x01\x02\x99'
        else:
          binary_content = '\x01\x02\x99'

        self.assertEqual(utils.base64encode(binary_content), 'AQKZ')
