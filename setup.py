#!/usr/bin/env python
'''
This file is part of cannon_cr3.

cannon_cr3 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

cannon_cr3 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with cannon_cr3. If not, see <http://www.gnu.org/licenses/>.

'''
from setuptools import setup

description = '''Package for extracting images and metadata out of Canon CR3 RAW image files'''

setup(
    name='canon_cr3',
    version='13mar2019',
    packages=['canon_cr3'],
    keywords='Canon cr3',
    url='https://github.com/superadm1n/CiscoAutomationFramework',
    license='GPLv3',
    description='Package for extracting images and metadata out of Canon CR3 RAW image files',
    long_description=description,
)
