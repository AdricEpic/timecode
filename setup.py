#!-*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGELOG')).read()

setup(
    name='timecode',
    version='0.3.1',
    description="SMPTE Time Code Manipulation Library",
    long_description='%s\n\n%s' % (README, CHANGES),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author=['Erkan Ozgur Yilmaz'],
    author_email=['eoyilmaz@gmail.com'],
    url='https://github.com/eoyilmaz/timecode',
    keywords=['video', 'timecode', 'smpte'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    test_suite="tests",
)
