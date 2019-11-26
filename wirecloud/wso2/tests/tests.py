# -*- coding: utf-8 -*-

# Copyright (c) 2019 Future Internet Consulting and Development Solutions S.L.
# Copyright (c) 2019 NEC Corporation.

# This file is part of Wirecloud WSO2 plugin.

# NOTE: This plugin is based on wirecloud-wso2 created by
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

import unittest

from wirecloud.wso2.tests.social_backend import WSO2SocialAuthBackendTestCase
from wirecloud.wso2.tests.plugins import WSO2PluginTestCase
from wirecloud.wso2.tests.proxy import IDMTokenProcessorTestCase
from wirecloud.wso2.tests.views import WSO2ViewTestCase


if __name__ == "__main__":
    unittest.main(verbosity=2)
