# -*- coding: utf-8 -*-

# Copyright (c) 2019 Future Internet Consulting and Development Solutions S.L.
# Copyright (c) 2019 NEC Corporation.

# This file is part of Wirecloud WSO2 plugin.

# NOTE: This plugin is based on wirecloud-keycloak created by
# Future Internet Consulting and Development Solutions S.L.

# Wirecloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Wirecloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Wirecloud.  If not, see <http://www.gnu.org/licenses/>.

import os
import setuptools

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name='wirecloud-wso2',
    version='0.1.0',
    author="NEC",
    author_email="",
    description="WireCloud extension supporting authentication with WSO2 IDM",
    long_description=read('./README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/NEC-FIWARE/wirecloud-wso2",
    packages=setuptools.find_packages(),
    license="AGPLv3+",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=(
        "wirecloud>=1.3.0"
    )
)
