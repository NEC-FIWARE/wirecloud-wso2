# WireCloud WSO2 plugin

[![](https://nexus.lab.fiware.org/repository/raw/public/badges/chapters/visualization.svg)](https://www.fiware.org/developers/catalogue/)
[![License badge](https://img.shields.io/badge/license-AGPLv3.0-blue.svg)](https://opensource.org/licenses/AGPL-3.0)<br/>
[![Build Status](https://travis-ci.com/NEC-FIWARE/wirecloud-wso2.svg?branch=master)](https://travis-ci.com/NEC-FIWARE/wirecloud-wso2)
[![Coverage Status](https://coveralls.io/repos/github/NEC-FIWARE/wirecloud-wso2/badge.svg)](https://coveralls.io/github/NEC-FIWARE/wirecloud-wso2)

This WireCloud plugin allows the usage of WSO2 as IDM for the authentication of WireCloud
users.

**NOTE:**
This plugin is based on [wirecloud-keycloak](https://github.com/Ficodes/wirecloud-keycloak)
created by Future Internet Consulting and Development Solutions S.L.

This plugin can be installed with pip as follows:

```
pip install -e git+https://github.com/NEC-FIWARE/wirecloud-wso2#egg=wirecloud-wso2
```

Or using the sources:

```
python setup.py develop
```

Once installed, it can be enabled by including *wirecloud.wso2* and *social_django*
in INSTALLED_APPS setting, and addiding *Wso2OAuth2* as an authentication backend.

```
INSTALLED_APPS += (
    # 'django.contrib.sites',
    # 'wirecloud.oauth2provider',
    'wirecloud.wso2',
    'haystack',
    'social_django'
)

AUTHENTICATION_BACKENDS = ('wirecloud.wso2.social_auth_backend.Wso2OAuth2',)
```

Finally the following settings need to be included in *setting.py* file.

```
WSO2_AM_SERVER = 'http://wso2.docker:9300'
SOCIAL_AUTH_WSO2_KEY = 'wirecloud'
SOCIAL_AUTH_WSO2_SECRET = '7667d30b-4e1a-4dfe-a040-0b6fdc4758f5'

```

These settings include:
* **WSO2_AM_SERVER**: URL of the WSO2 instance
* **SOCIAL_AUTH_WSO2_KEY**: Client ID of the WireCloud application
* **SOCIAL_AUTH_WSO2_SECRET**: Client secret of the WireCloud application

## Copyright and License

Copyright (c) 2019 Future Internet Consulting and Development Solutions S.L. 

Copyright (c) 2019-2020 NEC Corporation. 

WireCloud-WSO2 plugin is licensed under Affero General Public License (GPL) version 3.


