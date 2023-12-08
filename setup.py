# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2023/12/8 17:01
# @Version     : Python 3.6.4
import json
from pathlib import Path

from setuptools import find_packages, setup

VERSION_PATH = Path(__file__).parent / 'version.json'
version, description = json.loads(VERSION_PATH.read_text("utf-8"))
__version__ = f'1.0.{int(version)}'

setup(
    name='DRM',
    version=__version__,
    url='',
    license='None',
    author='LJQ',
    install_requires=[
        'dataclasses==0.8',
        'pycryptodome==3.11.0',
        'protobuf==4.21.0',
    ],
    description='Digital rights management',
    long_description='parse DRM keys',
    packages=find_packages(),
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    extras_require={},
    zip_safe=False
)
