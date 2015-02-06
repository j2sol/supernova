#!/usr/bin/python
#
# Copyright 2012 Major Hayden
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
from setuptools import setup


setup(
    name='superstack',
    version='1.0.0',
    author='Jesse Keating',
    author_email='jkeating@j2solutions.net',
    description="openstack client wrapper for multiple openstack environments",
    install_requires=['keyring', 'python-openstackclient'],
    packages=['superstack'],
    url='https://github.com/j2sol/superstack',
    entry_points={
        'console_scripts': [
            'superstack = superstack.executable:run_superstack',
            'superstack-keyring = superstack.executable:run_superstack_keyring'],
        }
    )
