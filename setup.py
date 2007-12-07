#!/usr/bin/env python
"""Distutils setup file"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

# Metadata
PACKAGE_NAME = "Presentable"
PACKAGE_VERSION = "0.1a1"
PACKAGES = ['peak', 'peak.ui']

def get_description():
    # Get our long description from the documentation
    f = file('README.txt')
    lines = []
    for line in f:
        if not line.strip():
            break     # skip to first blank line
    for line in f:
        if line.startswith('.. contents::'):
            break     # read to table of contents
        lines.append(line)
    f.close()
    return ''.join(lines)

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description="Skinnable GUIs, style sheets, and layout (for wx and others)",
    long_description = open('README.txt').read(), # get_description(),
    install_requires=['AddOns>=0.6'],
    author="Phillip J. Eby",
    author_email="peak@eby-sarna.com",
    license="PSF or ZPL",
    url="http://pypi.python.org/pypi/Presentable",
    test_suite = 'test_rendering',
    packages = PACKAGES,
    namespace_packages = PACKAGES,
)

