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

import base64
from urllib.parse import urljoin

from django.conf import settings
from social_core.backends.oauth import BaseOAuth2

WSO2_AUTHORIZATION_ENDPOINT = 'oauth2/authorize'
WSO2_ACCESS_TOKEN_ENDPOINT = 'oauth2/token'
WSO2_USER_DATA_ENDPOINT = 'oauth2/userinfo'


class Wso2OAuth2(BaseOAuth2):
    """Wso2 IDM OAuth authentication endpoint"""

    name = 'wso2'
    ID_KEY = 'username'

    WSO2_AM_SERVER = getattr(settings, 'WSO2_AM_SERVER', '')
    AUTHORIZATION_URL = urljoin(WSO2_AM_SERVER, WSO2_AUTHORIZATION_ENDPOINT)
    ACCESS_TOKEN_URL = urljoin(WSO2_AM_SERVER, WSO2_ACCESS_TOKEN_ENDPOINT)
    USER_DATA_URL = urljoin(WSO2_AM_SERVER, WSO2_USER_DATA_ENDPOINT)
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'
    SCOPE_VAR_NAME = 'FIWARE_EXTENDED_PERMISSIONS'
    DEFAULT_SCOPE = ['openid']
    EXTRA_DATA = [
        ('username', 'username'),
        ('refresh_token', 'refresh_token'),
        ('expires_in', 'expires'),
    ]

    def auth_headers(self):
        token = base64.urlsafe_b64encode(('{0}:{1}'.format(*self.get_key_and_secret()).encode())).decode()
        return {
            'Authorization': 'Basic {0}'.format(token)
        }

    def get_user_details(self, response):
        """Return user details from WSO2 account"""
        name = response.get('sub') or ''

        if 'role' in response:
            role = response.get('role').split(',')
        else:
            role = []

        superuser = "admin" in role

        return {
            'username': name,
            'email': response.get('email') or '',
            'fullname': name,
            'first_name': '',
            'last_name': '',
            'is_superuser': superuser,
            'is_staff': superuser,
        }

    def request_user_info(self, access_token):
        response = self.request(url=self.USER_DATA_URL, headers={'Authorization': 'Bearer {0}'.format(access_token)}, params={'schema': 'openid'})
        response.raise_for_status()
        return response.json()

    def user_data(self, access_token, *args, **kwargs):
        data = self.request_user_info(access_token)
        data['username'] = data.get('sub')

        return data

    def auth_complete_params(self, state=None):
        return {
            'grant_type': 'authorization_code',  # request auth code
            'code': self.data.get('code', ''),  # server response code
            'redirect_uri': self.get_redirect_uri(state)
        }
