"""Project setup and packaging for sanic-healthcheck."""

import os

from codecs import open  # for consistent encoding
from setuptools import setup, find_packages
import re


here = os.path.abspath(os.path.dirname(__file__))

# Load the package's __init__ file as a dictionary.
with open(os.path.join(here, 'sanic_healthcheck', '__init__.py'), 'r', 'utf-8') as f:
    pkg = {k: v for k, v in re.findall(
        r"^(__\w+__) = \'(.+)\'", f.read(), re.M)}

# Load the README
readme = ''
if os.path.exists('README.md'):
    with open('README.md', 'r', 'utf-8') as f:
        readme = f.read()

setup(
    name=pkg['__title__'],
    version=pkg['__version__'],
    description=pkg['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    url=pkg['__url__'],
    author=pkg['__author__'],
    author_email=pkg['__author_email__'],
    license=pkg['__license__'],
    packages=find_packages(exclude=['tests.*', 'tests']),
    python_requires='>=3.6',
    package_data={
        '': ['LICENSE'],
    },
    install_requires=[
        'sanic',
    ],
    zip_safe=False,
    keywords="sanic health healthcheck liveness readiness",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Sanic',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
