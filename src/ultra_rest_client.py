__author__ = 'jbodner'


# Zones
# create a primary zone
def create_primary_zone(zone_name):
    pass


# list zones for account
def get_zones_of_account(account_name):
    return get("/v1/accounts/" + account_name + "/zones")


# get zone metadata
def get_zone_metadata(zone_name):
    return get("/v1/zones/" + zone_name)


# delete a zone
def delete_zone(zone_name):
    pass


# RRSets
# list rrsets for a zone
def get_rrsets(zone_name):
    return get("/v1/zones/" + zone_name + "/rrsets")


# list rrsets by type for a zone
def get_rrsets_by_type(zone_name, rtype):
    return get("/v1/zones/" + zone_name + "/rrsets/" + rtype)


# create an rrset
def create_rrset(zone_name, rtype, owner_name, ttl, rdata):
    rrset = {"ttl":ttl, "rdata":rdata}
    return post("/v1/zones/"+zone_name+"/rrsets/"+rtype+"/"+owner_name, json.dumps(rrset))


# edit an rrset(PUT)
def edit_rrset(zone_name, rtype, owner_name, ttl, rdata):
    rrset = {"ttl": ttl, "rdata": rdata}
    return put("/v1/zones/" + zone_name + "/rrsets/" + rtype + "/" + owner_name, json.dumps(rrset))


# delete an rrset
def delete_rrset(zone_name, rtype, owner_name):
    return delete("/v1/zones/" + zone_name + "/rrsets/" + rtype + "/" + owner_name)


# Accounts
# get account details for user
def get_account_details():
    return get("/v1/accounts")


# Version
# get version
def version():
    return get("/v1/version")


# Status
# get status
def status():
    return get("/v1/status")


# store the URL and the access/refresh tokens as state
import httplib
import urllib
import json

url = "restapi.ultradns.com"
access_token = ""
refresh_token = ""
use_http = False


class AuthError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


def get_connection():
    global use_http
    if use_http:
        return httplib.HTTPConnection(url)
    else:
        return httplib.HTTPSConnection(url)


def fix_param_value(param_value):
    return urllib.quote(param_value.encode("utf-8"))

# Authentication
# We need the ability to take in a username and password and get
# an auth token and a refresh token. If any request fails due
# to an invalid auth token, refresh must be automatically invoked, the
# new auth token and refresh token stored, and the request tried again
# with the new auth token.
def auth(username, password, in_url=None):
    global url
    global access_token
    global refresh_token
    if in_url is not None:
        url = in_url
    h1 = get_connection()
    h1.request("GET",
               "/v1/authorization?username=" + fix_param_value(username) + "&password=" + fix_param_value(password))
    r1 = h1.getresponse()
    if r1.status == 200:
        json_body = json.loads(r1.read())
        access_token = json_body[u'accessToken']
        refresh_token = json_body[u'refreshToken']
    else:
        raise AuthError(json.loads(r1.read()))


def refresh():
    global access_token
    global refresh_token
    h1 = get_connection()
    h1.request("GET", "/v1/authorization/refresh")
    r1 = h1.getresponse()
    if r1.status == 200:
        json_body = json.loads(r1.read())
        access_token = json_body[u'accessToken']
        refresh_token = json_body[u'refreshToken']


def build_headers():
    return {"Content-type": "application/json", "Accept": "application/json", "Authorization": "Bearer " + access_token}


def get(uri):
    return do_call(uri, "GET")


def post_multi_part(uri, **parts):
    pass


def post(uri, json):
    return do_call(uri, "POST", json)


def put(uri, json):
    return do_call(uri, "PUT", json)


def delete(uri):
    return do_call(uri, "DELETE")


def do_call(uri, method, body=None, retry=True):
    h1 = get_connection()
    h1.request(method, uri, body=body, headers=build_headers())
    r1 = h1.getresponse()
    # bad access token = status 400,
    # body = {"errorCode":60001,"errorMessage":"invalid_grant:token not found, expired or invalid"}
    json_body = json.loads(r1.read())
    if retry and r1.status == 400 and json_body[u'errorCode'] == 60001:
        refresh()
        r1 = do_call(uri, method, body, False)
        json_body = json.loads(r1.read())
    return json_body


use_http = True
auth("bodnerdns", "Password2", "localhost:8080")
print version()
print status()
account_details = get_account_details()
account_name = account_details[u'list'][0][u'accountName']
print account_name
all_zones = get_zones_of_account(account_name)
first_zone_name = all_zones[u'list'][0][u'zoneProperties'][u'name']
print first_zone_name
print get_rrsets(first_zone_name)
print create_rrset(first_zone_name, "A", "foo", 300, ["1.2.3.4"])
print get_rrsets(first_zone_name)
print edit_rrset(first_zone_name, "A", "foo", 100, ["10.20.30.40"])
print get_rrsets(first_zone_name)
print delete_rrset(first_zone_name, "A", "foo")
print get_rrsets(first_zone_name)
