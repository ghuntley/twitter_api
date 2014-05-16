#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Twitter API
# Copyright (C) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Twitter API.
#
# Hive Twitter API is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Twitter API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Twitter API. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import appier

from twitter import user
from twitter import errors

BASE_URL = "https://api.twitter.com/"
""" The default base url to be used when no other
base url value is provided to the constructor """

CLIENT_KEY = None
""" The key (secret) value to be used for situations where
no client secret has been provided to the client """

REDIRECT_URL = "http://localhost:8080/oauth"
""" The redirect url used as default (fallback) value
in case none is provided to the api (client) """

class Api(
    appier.Api,
    user.UserApi
):

    def __init__(self, *args, **kwargs):
        appier.Api.__init__(self, *args, **kwargs)
        self.base_url = kwargs.get("base_url", BASE_URL)
        self.client_key = kwargs.get("client_key", CLIENT_KEY)
        self.redirect_url = kwargs.get("redirect_url", REDIRECT_URL)
        self.access_token = kwargs.get("access_token", None)

    def request(self, method, *args, **kwargs):
        try: result = method(*args, **kwargs)
        except appier.exceptions.HTTPError:
            raise errors.OAuthAccessError(
                "Problems using access token found must re-authorize"
            )
            raise

        return result

    def build_kwargs(self, kwargs, token = True):
        if token: kwargs["access_token"] = self.get_access_token()

    def get(self, url, token = True, **kwargs):
        self.build_kwargs(kwargs, token = token)
        return self.request(
            appier.get,
            url,
            params = kwargs
        )

    def post(self, url, token = True, data = None, data_j = None, data_m = None, **kwargs):
        self.build_kwargs(kwargs, token = token)
        return self.request(
            appier.post,
            url,
            params = kwargs,
            data = data,
            data_j = data_j,
            data_m = data_m
        )

    def put(self, url, token = True, data = None, data_j = None, data_m = None, **kwargs):
        self.build_kwargs(kwargs, token = token)
        return self.request(
            appier.put,
            url,
            params = kwargs,
            data = data,
            data_j = data_j,
            data_m = data_m
        )

    def delete(self, url, token = True, **kwargs):
        self.build_kwargs(kwargs, token = token)
        return self.request(
            appier.delete,
            url,
            params = kwargs
        )

    def get_access_token(self):
        if self.access_token: return self.access_token
        raise errors.OAuthAccessError(
            "No access token found must re-authorize"
        )

    def oauth_request(self):
        url = self.base_url + "oauth/request_token"
        contents = self.post(
            url,
            token = False,
            oauth_consumer_key = self.client_key,
            oauth_callback = self.redirect_url,
            oauth_signature_method = ""
            oauth_version = "1.0"
        )

    def oauth_autorize(self, state = None):
        url = "https://www.twitter.com/dialog/oauth"
        values = dict(
            client_id = self.client_id,
            redirect_uri = self.redirect_url,
            response_type = "code",
            scope = " ".join(self.scope)
        )
        if state: values["state"] = state
        data = appier.urlencode(values)
        url = url + "?" + data
        return url

    def oauth_access(self, code, long = True):
        url = self.base_url + "oauth/access_token"
        contents = self.post(
            url,
            token = False,
            client_id = self.client_id,
            client_secret = self.client_secret,
            grant_type = "authorization_code",
            redirect_uri = self.redirect_url,
            code = code
        )
        contents = contents.decode("utf-8")
        contents = appier.parse_qs(contents)
        self.access_token = contents["access_token"][0]
        self.trigger("access_token", self.access_token)
        if long: self.access_token = self.oauth_long_lived(self.access_token)
        return self.access_token

    def oauth_long_lived(self, short_token):
        url = self.base_url + "oauth/access_token"
        contents = self.post(
            url,
            token = False,
            client_id = self.client_id,
            client_secret = self.client_secret,
            grant_type = "fb_exchange_token",
            redirect_uri = self.redirect_url,
            fb_exchange_token = short_token,
        )
        contents = contents.decode("utf-8")
        contents = appier.parse_qs(contents)
        self.access_token = contents["access_token"][0]
        self.trigger("access_token", self.access_token)
        return self.access_token