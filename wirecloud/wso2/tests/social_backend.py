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

from copy import deepcopy
import json
import unittest

from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock

import django.dispatch


def signal_decorator(signal, sender=None):
    def mock_decorator(funct):
        def wrapper(sender, instance, created, **kwargs):
            funct(sender, instance, created)

        return wrapper
    return mock_decorator

class Response():
    def raise_for_status():
        return

    def json():
        return ({'sub': 'username'})

class BaseOAuthMock():

    STRATEGY = None
    def __init__(self, strategy):
        self.STRATEGY = strategy

    def get_key_and_secret(self):
        return ('client', 'secret')

    def request(self, url, headers, params):
        return (Response)

class WSO2SocialAuthBackendTestCase(TestCase):

    WSO2_AM_SERVER = 'http://server'

    CLIENT_ID = 'client'
    SECRET = 'secret'

    TOKEN_INFO = {
        'sub': 'username',
        'email': 'email@email.com'
    }

    DETAILS = {
        'username': 'username',
        'email': 'email@email.com',
        'fullname': 'username',
        'first_name': '',
        'last_name': '',
        'is_superuser': False,
        'is_staff': False
    }

    def setUp(self):
        self._strategy = MagicMock()

        import django.conf
        self._old_settings = django.conf.settings
        self._settings = MagicMock(
            WSO2_AM_SERVER=self.WSO2_AM_SERVER,
            SOCIAL_AUTH_WSO2_KEY=self.CLIENT_ID,
            SOCIAL_AUTH_WSO2_SECRET=self.SECRET
        )

        django.conf.settings = self._settings

        # Mock post_save signal
        from django.dispatch import receiver
        self._receiver = receiver

        django.dispatch.receiver = signal_decorator

    def tearDown(self):
        import django.conf
        django.conf.settings = self._old_settings
        django.dispatch.receiver = self._receiver

    def _mock_module(self):
        from wirecloud.wso2 import social_auth_backend

        social_auth_backend.settings = self._settings
        oauth2 = social_auth_backend.Wso2OAuth2(self._strategy)
        return oauth2

    @patch('social_core.backends.oauth.BaseOAuth2', new=BaseOAuthMock)
    def test_class_params(self):
        oauth2 = self._mock_module()

        self.assertEqual(oauth2.WSO2_AM_SERVER, 'http://server')

        self.assertEqual(oauth2.ACCESS_TOKEN_URL, 'http://server/oauth2/token')
        self.assertEqual(oauth2.AUTHORIZATION_URL, 'http://server/oauth2/authorize')

    def test_get_auth_headers(self):
        oauth2 = self._mock_module()
        headers = oauth2.auth_headers()

        self.assertEqual(headers, {
            'Authorization': 'Basic Y2xpZW50OnNlY3JldA=='
        })

    def _test_get_user_details(self, resource, expected_details):
        oauth2 = self._mock_module()
        details = oauth2.get_user_details(resource)

        self.assertEqual(details, expected_details)
        self.assertEquals(self._strategy, oauth2.STRATEGY)

    @patch('social_core.backends.oauth.BaseOAuth2', new=BaseOAuthMock)
    def test_get_user_details_regular(self):
        self._test_get_user_details(self.TOKEN_INFO, self.DETAILS)

    @patch('social_core.backends.oauth.BaseOAuth2', new=BaseOAuthMock)
    def test_get_user_details_admin(self):
        resource = deepcopy(self.TOKEN_INFO)
        details = deepcopy(self.DETAILS)

        resource['role'] = "Internal/everyone,admin,test"

        details['is_superuser'] = True
        details['is_staff'] = True

        self._test_get_user_details(resource, details)

    @patch('social_core.backends.oauth.BaseOAuth2', new=BaseOAuthMock)
    def test_get_user_info(self):
        oauth2 = self._mock_module()
        user_info = oauth2.user_data('token')

        self.assertEqual(user_info, {'sub': 'username', 'username': 'username'})

if __name__ == "__main__":
    unittest.main(verbosity=2)
