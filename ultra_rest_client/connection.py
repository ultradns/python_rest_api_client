# Copyright 2000 - 2013 NeuStar, Inc.All rights reserved.
# NeuStar, the Neustar logo and related names and logos are registered
# trademarks, service marks or tradenames of NeuStar, Inc. All other
# product names, company names, marks, logos and symbols may be trademarks
# of their respective owners.
__author__ = 'Jon Bodner'

# store the URL and the access/refresh tokens as state
import requests
from .about import get_client_user_agent

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
        payload = {"grant_type":"refresh_token","refresh_token":self.refresh_token}
        r1 = requests.post(h1+"/v1/authorization/token", data=payload)
        if r1.status_code == requests.codes.OK:
            json_body = r1.json()
            self.access_token = json_body[u'accessToken']
            self.refresh_token = json_body[u'refreshToken']
        else:
            raise AuthError(r1.json())

    def _build_headers(self, content_type):
        result = {"Accept": "application/json",
                  "Authorization": "Bearer " + self.access_token,
                  "User-Agent": get_client_user_agent()}
        if content_type != "":
            result["Content-type"] = content_type
        return result

    def get(self, uri, params=None):
        if params is None:
            params = {}
        return self._do_call(uri, "GET", params=params)

    def post_multi_part(self, uri, files):
        #use empty string for content type so we don't set it
        return self._do_call(uri, "POST", files=files, content_type="")

    def post(self, uri, json=None):
        if json is not None:
            return self._do_call(uri, "POST", body=json)
        else:
            return self._do_call(uri, "POST")

    def put(self, uri, json):
        return self._do_call(uri, "PUT", body=json)

    def patch(self, uri, json):
        return self._do_call(uri, "PATCH", body=json)

    def delete(self, uri):
        return self._do_call(uri, "DELETE")

    def _do_call(self, uri, method, params=None, body=None, retry=True, files=None, content_type = "application/json"):
        h1 = self._get_connection()
        r1 = requests.request(method, h1+uri, params=params, data=body, headers=self._build_headers(content_type), files=files)
        # bad access token = status 400,
        # body = {"errorCode":60001,"errorMessage":"invalid_grant:token not found, expired or invalid"}
        if r1.status_code == requests.codes.NO_CONTENT:
            return {}
        # if the content-type is text/plain just return the text
        if r1.headers['Content-Type'] == 'text/plain':
            return r1.text
        json_body = r1.json()
        # if this is a background task, add the task id to the body
        if r1.status_code == requests.codes.ACCEPTED:
            json_body['task_id'] = r1.headers['x-task-id']
        if type(json_body) is dict:
            if retry and u'errorCode' in json_body and json_body[u'errorCode'] == 60001:
                self._refresh()
                json_body = self._do_call(uri, method, params, body, False)
            #disabling error raising for now, because it only happens for batch
            #because all other errors are returned in a list, not in a dict
            #should have been raising errors for those, too, but haven't been
            #elif r1.status_code >= requests.codes.BAD_REQUEST:
            #    raise RestError(json_body)
        return json_body
