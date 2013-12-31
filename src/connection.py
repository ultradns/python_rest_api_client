# Copyright 2000 - 2013 NeuStar, Inc.All rights reserved.
# NeuStar, the Neustar logo and related names and logos are registered
# trademarks, service marks or tradenames of NeuStar, Inc. All other
# product names, company names, marks, logos and symbols may be trademarks
# of their respective owners.
__author__ = 'Jon Bodner'

# store the URL and the access/refresh tokens as state
import requests

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
            return "http://"+ self.host
        else:
            return "https://"+ self.host

    # Authentication
    # We need the ability to take in a username and password and get
    # an auth token and a refresh token. If any request fails due
    # to an invalid auth token, refresh must be automatically invoked, the
    # new auth token and refresh token stored, and the request tried again
    # with the new auth token.
    def auth(self, username, password):
        h1 = self._get_connection()
        payload = {"grant_type":"password", "username":username, "password":password}
        r1 = requests.post(h1+"/v1/authorization/token",data=payload)
        if r1.status_code == requests.codes.OK:
            json_body = r1.json()
            self.access_token = json_body[u'accessToken']
            self.refresh_token = json_body[u'refreshToken']
        else:
            raise AuthError(r1.json())

    def _refresh(self):
        h1 = self._get_connection()
        payload = {"grant_type":"refresh_token","refreshToken":self.refresh_token}
        r1 = requests.post(h1+"/v1/authorization/token", data=payload)
        if r1.status_code == requests.codes.OK:
            json_body = r1.json()
            self.access_token = json_body[u'accessToken']
            self.refresh_token = json_body[u'refreshToken']
        else:
            raise AuthError(r1.json())

    def _build_headers(self):
        return {"Content-type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer " + self.access_token}

    def get(self, uri, params={}):
        return self._do_call(uri, "GET", params=params)

    def post_multi_part(self, uri, **parts):
        pass

    def post(self, uri, json):
        return self._do_call(uri, "POST", body=json)

    def put(self, uri, json):
        return self._do_call(uri, "PUT", body=json)

    def delete(self, uri):
        return self._do_call(uri, "DELETE")

    def _do_call(self, uri, method, params=None, body=None, retry=True):
        h1 = self._get_connection()
        r1 = requests.request(method, h1+uri, params=params, data=body, headers=self._build_headers())
        # bad access token = status 400,
        # body = {"errorCode":60001,"errorMessage":"invalid_grant:token not found, expired or invalid"}
        if r1.status_code == requests.codes.NO_CONTENT:
            return {}
        json_body = r1.json()
        if type(json_body) is dict:
            if retry and r1.status_code not in (requests.codes.BAD_REQUEST, requests.codes.UNAUTHORIZED) and u'errorCode' in json_body and json_body[u'errorCode'] == 60001:
                self._refresh()
                r1 = self._do_call(uri, method, params, body, False)
                json_body = r1.json()
            elif r1.status_code >= requests.codes.BAD_REQUEST:
                raise RestError(json_body)
        return json_body
