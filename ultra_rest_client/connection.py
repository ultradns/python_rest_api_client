# Copyright 2023 Vercara. All rights reserved.
# Vercara, the Vercara logo and related names and logos are registered
# trademarks, service marks or tradenames of Vercara, Inc. All other
# product names, company names, marks, logos and symbols may be trademarks
# of their respective owners.
__author__ = 'UltraDNS'

# store the URL and the access/refresh tokens as state
import requests
import time
from .about import get_client_user_agent

class AuthError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return str(self.message)


class RestError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return str(self.message)


class RestApiConnection:
    def __init__(self, use_http=False, host="api.ultradns.com", access_token: str = "", refresh_token: str = ""):
        self.use_http = use_http
        self.host = host
        self.access_token = access_token
        self.refresh_token = refresh_token

    def _get_connection(self):
        if self.host.startswith("https://") or self.host.startswith("http://"):
            return self.host
        else:
            protocol = "http://" if self.use_http else "https://"
            return protocol + self.host

    # Authentication
    # We need the ability to take in a username and password and get
    # an auth token and a refresh token. If any request fails due
    # to an invalid auth token, refresh must be automatically invoked, the
    # new auth token and refresh token stored, and the request tried again
    # with the new auth token.

    def auth(self, username, password):
        host = self._get_connection()
        payload = {
            "grant_type":"password",
            "username":username,
            "password":password
        }
        response = requests.post(f"{host}/v1/authorization/token", data=payload)
        if response.status_code == requests.codes.OK:
            json_body = response.json()
            self.access_token = json_body.get('accessToken')
            self.refresh_token = json_body.get('refreshToken')
        else:
            raise AuthError(response.json())

    def _refresh(self):
        host = self._get_connection()
        payload = {
            "grant_type":"refresh_token",
            "refresh_token":self.refresh_token
        }
        response = requests.post(f"{host}/v1/authorization/token", data=payload)
        if response.status_code == requests.codes.OK:
            json_body = response.json()
            self.access_token = json_body.get('accessToken')
            self.refresh_token = json_body.get('refreshToken')
        else:
            raise AuthError(response.json())

    def _build_headers(self, content_type):
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": get_client_user_agent()
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def get(self, uri, params=None):
        params = params or {}
        return self._do_call(uri, "GET", params=params)

    def post_multi_part(self, uri, files):
        #use empty string for content type so we don't set it
        return self._do_call(uri, "POST", files=files, content_type=None)

    def post(self, uri, json=None):
        return self._do_call(uri, "POST", body=json) if json is not None else self._do_call(uri, "POST")

    def put(self, uri, json):
        return self._do_call(uri, "PUT", body=json)

    def patch(self, uri, json):
        return self._do_call(uri, "PATCH", body=json)

    def delete(self, uri):
        return self._do_call(uri, "DELETE")

    def _do_call(self, uri, method, params=None, body=None, retry=True, files=None, content_type="application/json"):
        host = self._get_connection()
        response = requests.request(
            method,
            host + uri,
            params=params,
            data=body,
            headers=self._build_headers(content_type),
            files=files
        )
        if response.status_code == requests.codes.NO_CONTENT:
            return {}

        if response.status_code == requests.codes.TOO_MANY:
            time.sleep(1)
            return self._do_call(uri, method, params, body, False)

        # some endpoints have no content-type header
        if 'content-type' not in response.headers:
            response.headers['content-type'] = 'none'

        # if the content-type is text/plain just return the text
        if response.headers.get('content-type') == 'text/plain':
            return response.text

        # Return the bytes. Zone exports produce zip files when done in batch.
        if response.headers.get('content-type') == 'application/zip':
            return response.content

        json_body = {}
        try:
          json_body = response.json()

          # if this is a background task, add the task id (or location) to the body
          if response.status_code == requests.codes.ACCEPTED:
            if 'x-task-id' in response.headers:
              json_body.update({"task_id": response.headers['x-task-id']})
            if 'location' in response.headers:
              json_body.update({"location": response.headers['location']})

        except requests.exceptions.JSONDecodeError:
          json_body = {}

        if isinstance(json_body, dict) and retry and json_body.get('errorCode') == 60001:
            self._refresh()
            return self._do_call(uri, method, params, body, False)

        return json_body
