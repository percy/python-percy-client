#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


requirements = [
    'requests>=2.14.0'
]

test_requirements = [
    'requests-mock',
]

setup(
    name='percy',
    version='2.0.1',
    description='Python client library for visual regression testing with Percy (https://percy.io).',
    author='Perceptual Inc.',
    author_email='team@percy.io',
    url='https://github.com/percy/python-percy-client',
    packages=[
        'percy',
    ],
    package_dir={'percy': 'percy'},
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    zip_safe=False,
    keywords='percy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
