# -*- coding: utf-8 -*-
"""setup.py -- setup file for nonobvious
"""
import sys
import os

from setuptools import setup, find_packages

PYVERSION = float('%s.%s' % (sys.version_info[0], sys.version_info[1]))
PATH = os.path.abspath(os.path.dirname(__file__))

INSTALL_REQUIRES = [
    line
    for line in
    open(os.path.join(PATH, 'requirements.txt')).read().splitlines()
    if not line.startswith('-') and not line.startswith('#')
]

TESTS_REQUIRE = [
    line
    for line in
    open(os.path.join(PATH, 'test-requirements.txt')).read().splitlines()
    if not line.startswith('-') and not line.startswith('#')
]

README = os.path.join(PATH, 'README.rst')

SETUP = dict(
    name = "nonobvious",
    packages = find_packages(),
    install_requires = INSTALL_REQUIRES,
    tests_require = TESTS_REQUIRE,
    test_suite = 'nose.collector',

    package_data = {
        '': ['*.txt', '*.html'],
    },
    zip_safe = False,

    version = "0.1",
    description = "A simple, but non-obvious approach to setting boundaries.",
    long_description = open(README).read(),
    author = "David Eyk",
    author_email = "david.eyk@gmail.com",
    url = "http://github.com/eykd/nonobvious",
    license = 'BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries',
    ],
)

setup(**SETUP)
