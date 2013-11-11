# Copyright 2000 - 2013 NeuStar, Inc.All rights reserved.
# NeuStar, the Neustar logo and related names and logos are registered
# trademarks, service marks or tradenames of NeuStar, Inc. All other
# product names, company names, marks, logos and symbols may be trademarks
# of their respective owners.
__author__ = 'Jon Bodner'

# store the URL and the access/refresh tokens as state
import httplib
import urllib
import json


class AuthError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class RestError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class RestApiConnection:
    def __init__(self, use_http=False, host="restapi.ultradns.com"):
        self.use_http = use_http
        self.host = host
        self.access_token = ""
        self.refresh_token = ""

    def _get_connection(self):
        if self.use_http:
            return httplib.HTTPConnection(self.host)
        else:
            return httplib.HTTPSConnection(self.host)

    # Authentication
    # We need the ability to take in a username and password and get
    # an auth token and a refresh token. If any request fails due
    # to an invalid auth token, refresh must be automatically invoked, the
    # new auth token and refresh token stored, and the request tried again
    # with the new auth token.
    def auth(self, username, password):
        h1 = self._get_connection()
        h1.request("GET",
                   "/v1/authorization?username=" + fix_param_value(username) + "&password=" + fix_param_value(password))
        r1 = h1.getresponse()
        if r1.status == 200:
            json_body = json.loads(r1.read())
            self.access_token = json_body[u'accessToken']
            self.refresh_token = json_body[u'refreshToken']
        else:
            raise AuthError(json.loads(r1.read()))

    def _refresh(self):
        h1 = self._get_connection()
        h1.request("GET", "/v1/authorization/refresh")
        r1 = h1.getresponse()
        if r1.status == 200:
            json_body = json.loads(r1.read())
            self.access_token = json_body[u'accessToken']
            self.refresh_token = json_body[u'refreshToken']
        else:
            raise AuthError(json.loads(r1.read()))

    def _build_headers(self):
        return {"Content-type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer " + self.access_token}

    def get(self, uri):
        return self._do_call(uri, "GET")

    def post_multi_part(self, uri, **parts):
        pass

    def post(self, uri, json):
        return self._do_call(uri, "POST", json)

    def put(self, uri, json):
        return self._do_call(uri, "PUT", json)

    def delete(self, uri):
        return self._do_call(uri, "DELETE")

    def _do_call(self, uri, method, body=None, retry=True):
        h1 = self._get_connection()
        h1.request(method, uri, body=body, headers=self._build_headers())
        r1 = h1.getresponse()
        # bad access token = status 400,
        # body = {"errorCode":60001,"errorMessage":"invalid_grant:token not found, expired or invalid"}
        return_body = r1.read()
        if return_body not in(None, ""):
            json_body = json.loads(return_body)
            if type(json_body) is dict:
                if retry and r1.status == 400 and json_body[u'errorCode'] == 60001:
                    self._refresh()
                    r1 = self._do_call(uri, method, body, False)
                    json_body = json.loads(r1.read())
                elif r1.status >= 400:
                    raise RestError(json_body)
            return json_body
        else:
            return "{}"


#utility methods
def fix_param_value(param_value):
    return urllib.quote(param_value.encode("utf-8"))
