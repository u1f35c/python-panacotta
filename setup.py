#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Jonathan McDowell <noodles@earth.li>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import setuptools

with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup(
    name='panacotta',
    version="0.2",
    author='Jonathan McDowell',
    author_email='noodles@earth.li',
    description='Python API for controlling Panasonic Blu-Ray players',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/u1f35c/python-panacotta',
    packages=setuptools.find_packages(),
    scripts=[],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
)
