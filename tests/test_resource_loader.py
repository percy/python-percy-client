import unittest
import os

from percy.resource_loader import ResourceLoader

TEST_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testdata')

class FakeWebdriver(object):
    page_source = 'foo'
    current_url = '/'


class FakeWebdriverAbsoluteUrl(object):
    page_source = 'foo'
    current_url = 'http://testserver/'


class TestPercyResourceLoader(unittest.TestCase):
    def test_blank_loader(self):
        resource_loader = ResourceLoader()
        assert resource_loader.build_resources == []
        resource_loader = ResourceLoader(webdriver=FakeWebdriver())
        assert resource_loader.snapshot_resources[0].resource_url == '/'

    def test_build_resources(self):
        root_dir = os.path.join(TEST_FILES_DIR, 'static')
        resource_loader = ResourceLoader(root_dir=root_dir, base_url='/assets/')
        resources = resource_loader.build_resources
        resource_urls = sorted([r.resource_url for r in resources])
        assert resource_urls == [
            '/assets/app.js',
            '/assets/images/jellybeans.png',
            '/assets/images/logo.png',
            '/assets/styles.css',
        ]

    def test_absolute_snapshot_resources(self):
        resource_loader = ResourceLoader(webdriver=FakeWebdriverAbsoluteUrl())
        assert resource_loader.snapshot_resources[0].resource_url == '/'
