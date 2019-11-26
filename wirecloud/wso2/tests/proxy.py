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

from importlib import reload
from io import BytesIO

import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock

from wirecloud.proxy.utils import ValidationError


def translation_mock(text):
    return text


class IDMTokenProcessorTestCase(TestCase):

    def _text_proxy_processor(self, request):
        import wirecloud.wso2.proxy
        reload(wirecloud.wso2.proxy)

        wirecloud.wso2.proxy._ = translation_mock
        wirecloud.wso2.proxy.IDM_SUPPORT_ENABLED = True
        self._strategy = MagicMock()
        wirecloud.wso2.proxy.STRATEGY = self._strategy

        processor = wirecloud.wso2.proxy.IDMTokenProcessor()
        processor.process_request(request)

    @patch('django.conf.settings', new=MagicMock(INSTALLED_APPS=(
            'wirecloud.wso2',
            'social_django'
        ), SOCIAL_AUTH_WSO2_KEY='key', SOCIAL_AUTH_WSO2_SECRET='secret'))
    @patch('wirecloud.wso2.utils.build_backend', new=MagicMock())
    @patch('wirecloud.wso2.utils.build_version_hash', new=MagicMock())
    @patch('wirecloud.wso2.utils.load_strategy', new=MagicMock())
    def test_proxy_no_headers(self):
        request = {
            'headers': []
        }

        from wirecloud.wso2.proxy import IDMTokenProcessor
        processor = IDMTokenProcessor()

        processor.process_request(request)

    @patch('django.conf.settings', new=MagicMock(INSTALLED_APPS=(
            'wirecloud.wso2',
            'social_django'
        ), SOCIAL_AUTH_WSO2_KEY='key', SOCIAL_AUTH_WSO2_SECRET='secret'))
    @patch('wirecloud.wso2.utils.build_backend', new=MagicMock())
    @patch('wirecloud.wso2.utils.build_version_hash', new=MagicMock())
    @patch('wirecloud.wso2.utils.load_strategy', new=MagicMock())
    def test_proxy_user_source_token(self):
        oauth_info = MagicMock(access_token='token')
        oauth_info.access_token_expired.return_value = False

        user = MagicMock()
        user.social_auth.get.return_value = oauth_info

        request = {
            'user': user,
            'headers': {
                'fiware-oauth-token': 'token1',
                'fiware-oauth-header-name': 'Authorization'
            },
            'workspace': {}
        }

        self._text_proxy_processor(request)

        # Validate oauth info calls
        user.social_auth.get.assert_called_once_with(provider='wso2')
        oauth_info.access_token_expired.assert_called_once_with()
        self.assertEqual(0, oauth_info.refresh_token.call_count)

        # Validate headers
        self.assertEqual({
            'Authorization': 'Bearer token'
        }, request['headers'])

    @patch('django.conf.settings', new=MagicMock(INSTALLED_APPS=(
            'wirecloud.wso2',
            'social_django'
        ), SOCIAL_AUTH_WSO2_KEY='key', SOCIAL_AUTH_WSO2_SECRET='secret'))
    @patch('wirecloud.wso2.utils.build_backend', new=MagicMock())
    @patch('wirecloud.wso2.utils.build_version_hash', new=MagicMock())
    @patch('wirecloud.wso2.utils.load_strategy', new=MagicMock())
    def test_proxy_workspace_owner_token_not_filtered(self):
        oauth_info = MagicMock(access_token='token')
        oauth_info.access_token_expired.return_value = True

        user = MagicMock()
        user.social_auth.get.return_value = oauth_info

        workspace = MagicMock(creator=user)
        request = {
            'url': 'http://proxy.com/url/?id=1',
            'headers': {
                'fiware-oauth-token': 'token1',
                'fiware-oauth-header-name': 'Authorization',
                'fiware-oauth-source': 'workspaceowner',
                'fiware-oauth-get-parameter': 'x-api-key',
                'fiware-oauth-body-pattern': '{token}'
            },
            'workspace': workspace,
            'data': BytesIO('The token is {token}'.encode('utf8'))
        }

        self._text_proxy_processor(request)

        # Validate oauth info calls
        user.social_auth.get.assert_called_once_with(provider='wso2')
        oauth_info.access_token_expired.assert_called_once_with()
        oauth_info.refresh_token.assert_called_once_with(self._strategy)

        self.assertEqual({
            'Authorization': 'Bearer token', 'content-length': '18'
        }, request['headers'])
        self.assertEqual('http://proxy.com/url/?id=1&x-api-key=token', request['url'])
        self.assertEqual(b'The token is token', request['data'].read())

    def _test_validation_error(self, msg, request):
        error = None
        try:
            self._text_proxy_processor(request)
        except Exception as e:
            error = e

        self.assertTrue(isinstance(error, ValidationError))
        self.assertEqual(msg, str(error))

    @patch('django.conf.settings', new=MagicMock(INSTALLED_APPS=()))
    @patch('wirecloud.wso2.utils.build_backend', new=MagicMock())
    @patch('wirecloud.wso2.utils.build_version_hash', new=MagicMock())
    @patch('wirecloud.wso2.utils.load_strategy', new=MagicMock())
    def test_idm_not_enabled(self):
        request = {
            'headers': {
                'fiware-oauth-token': 'token1',
                'fiware-oauth-header-name': 'Authorization'
            },
            'workspace': {}
        }

        import wirecloud.wso2.proxy
        reload(wirecloud.wso2.proxy)

        wirecloud.wso2.proxy._ = translation_mock
        wirecloud.wso2.proxy.IDM_SUPPORT_ENABLED = False

        processor = wirecloud.wso2.proxy.IDMTokenProcessor()
        error = None
        try:
            processor.process_request(request)
        except Exception as e:
            error = e

        self.assertTrue(isinstance(error, ValidationError))
        self.assertEqual('IdM support not enabled', str(error))

    def test_workspace_not_included(self):
        request = {
            'headers': {
                'fiware-oauth-token': 'token1',
                'fiware-oauth-header-name': 'Authorization'
            },
            'workspace': None
        }

        self._test_validation_error(
            'IdM tokens can only be inyected on Ajax requests coming from authorized widgets', request)

    def test_invalid_source(self):
        request = {
            'headers': {
                'fiware-oauth-token': 'token1',
                'fiware-oauth-header-name': 'Authorization',
                'fiware-oauth-source': 'invalid',
            },
            'workspace': {}
        }

        self._test_validation_error(
            'Invalid FIWARE OAuth token source', request)

    def test_missing_token(self):
        oauth_info = MagicMock(access_token=None)
        oauth_info.access_token_expired.return_value = True

        user = MagicMock()
        user.social_auth.get.return_value = oauth_info

        request = {
            'user': user,
            'headers': {
                'fiware-oauth-token': 'token1',
                'fiware-oauth-header-name': 'Authorization'
            },
            'workspace': {}
        }

        self._test_validation_error(
            'Current user has not an active FIWARE profile', request)

if __name__ == "__main__":
    unittest.main(verbosity=2)
