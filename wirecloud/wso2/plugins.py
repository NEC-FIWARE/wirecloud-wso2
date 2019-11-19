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

from django.conf import settings
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page

from wirecloud.wso2.utils import build_version_hash, build_backend, get_social_auth_model
from wirecloud.platform.plugins import WirecloudPlugin

get_version_hash = build_version_hash()

try:
    WSO2_SOCIAL_AUTH_BACKEND = build_backend()

    IDM_SUPPORT_ENABLED = 'wirecloud.wso2' in settings.INSTALLED_APPS and 'social_django' in settings.INSTALLED_APPS  \
        and getattr(settings, 'SOCIAL_AUTH_WSO2_KEY', None) is not None and getattr(settings, 'SOCIAL_AUTH_WSO2_SECRET', None) is not None

except:
    IDM_SUPPORT_ENABLED = False


def auth_wso2_token(auth_type, token):

    from social_django.models import UserSocialAuth
    user_data = WSO2_SOCIAL_AUTH_BACKEND.user_data(token)
    return UserSocialAuth.objects.get(provider='wso2', uid=user_data['username']).user


class Wso2Plugin(WirecloudPlugin):
    def get_urls(self):

        if IDM_SUPPORT_ENABLED:
            from wirecloud.wso2.views import oauth_discovery
            return (
                url('^.well-known/oauth$', cache_page(7 * 24 * 60 * 60, key_prefix='well-known-oauth-%s' % get_version_hash())(oauth_discovery), name='oauth.discovery'),
            )
        else:
            return ()

    def get_api_auth_backends(self):

        if IDM_SUPPORT_ENABLED:
            return {
                'Bearer': auth_wso2_token,
            }
        else:
            return {}

    def get_constants(self):
        constants = {}
        if IDM_SUPPORT_ENABLED:
            global WSO2_SOCIAL_AUTH_BACKEND
            constants["WSO2_AM_SERVER"] = WSO2_SOCIAL_AUTH_BACKEND.WSO2_AM_SERVER

        return constants

    def get_proxy_processors(self):
        if not IDM_SUPPORT_ENABLED:
            return ()

        return ('wirecloud.wso2.proxy.IDMTokenProcessor',)

    def get_platform_context_definitions(self):
        # Using default FIWARE token parameter for compatibility with existing widgets
        return {
            'fiware_token_available': {
                'label': _('FIWARE token available'),
                'description': _('Indicates if the current user has associated a FIWARE auth token that can be used for accessing other FIWARE resources'),
            },
        }

    def get_platform_context_current_values(self, user, **kwargs):
        # Work around bug when running manage.py compress
        fiware_token_available = IDM_SUPPORT_ENABLED and user.is_authenticated() and user.social_auth.filter(provider='wso2').exists()
        return {
            'fiware_token_available': fiware_token_available
        }

    def get_django_template_context_processors(self):
        context = {}

        # Using FIWARE name in context for compatibility with existing templates
        if IDM_SUPPORT_ENABLED:
            context["WSO2_AM_SERVER"] = getattr(settings, "WSO2_AM_SERVER", '')
        else:
            context["WSO2_AM_SERVER"] = None

        return context

