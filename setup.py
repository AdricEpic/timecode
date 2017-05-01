#!-*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGELOG')).read()

VERSION_FPATH = os.path.join(here, "timecode", "__version__.py")
with open(VERSION_FPATH, 'r') as vf:
    VERSION_STR_LINE = vf.read()
VERSION_RE = r"^__version__ = ['\"](?P<version>[^'\"].*)['\"]"
ver_search = re.search(VERSION_RE, VERSION_STR_LINE)
if ver_search:
    VERSION = ver_search.group("version")
else:
    raise RuntimeError("Unable to find version string in {}".format(VERSION_FPATH))

setup(
    name='timecode',
    version=VERSION,
    description="SMPTE Time Code Manipulation Library",
    long_description='%s\n\n%s' % (README, CHANGES),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author='Erkan Ozgur Yilmaz, Adric Worley',
    author_email=['eoyilmaz@gmail.com', 'adric@originaladric.com'],
    url='https://github.com/eoyilmaz/timecode',
    keywords=['video', 'timecode', 'smpte'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    test_suite="tests",
    tests_require=['pytest>=3.0.7']
)
