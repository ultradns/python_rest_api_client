# Copyright 2000 - 2013 NeuStar, Inc.All rights reserved.
# NeuStar, the Neustar logo and related names and logos are registered
# trademarks, service marks or tradenames of NeuStar, Inc. All other
# product names, company names, marks, logos and symbols may be trademarks
# of their respective owners.
__author__ = 'Jon Bodner'
import connection
import json
import urllib


class RestApiClient:
    def __init__(self, username, password, use_http=False, host="restapi.ultradns.com"):
        """Initialize a Rest API Client.

        Arguments:
        username -- The username of the user
        password -- The password of the user

        Keyword Arguments:
        use_http -- For internal testing purposes only, lets developers use http instead of https.
        host -- Allows you to point to a server other than the production server.

        """
        self.rest_api_connection = connection.RestApiConnection(use_http, host)
        self.rest_api_connection.auth(username, password)

    # Zones
    # create a primary zone
    def create_primary_zone(self, account_name, zone_name):
        """Creates a new primary zone.

        Arguments:
        account_name -- The name of the account that will contain this zone.
        zone_name -- The name of the zone.  It must be unique.

        """
        zone_properties = {"name": zone_name, "accountName": account_name, "type": "PRIMARY"}
        primary_zone_info = {"forceImport": True, "createType": "NEW"}
        zone_data = {"properties": zone_properties, "primaryCreateInfo": primary_zone_info}
        return self.rest_api_connection.post("/v1/zones", json.dumps(zone_data))

    # list zones for account
    def get_zones_of_account(self, account_name, q=None, **kwargs):
        """Returns a list of zones for the specified account.

        Arguments:
        account_name -- The name of the account.

        Keyword Arguments:
        q -- The search parameters, in a dict.  Valid keys are:
             name - substring match of the zone name
             zone_type - one of:
                PRIMARY
                SECONDARY
                ALIAS
        sort -- The sort column used to order the list. Valid values for the sort field are:
                NAME
                ACCOUNT_NAME
                RECORD_COUNT
                ZONE_TYPE
        reverse -- Whether the list is ascending(False) or descending(True)
        offset -- The position in the list for the first returned element(0 based)
        limit -- The maximum number of rows to be returned.

        """
        uri = "/v1/accounts/" + account_name + "/zones"
        params = build_params(q, kwargs)
        return self.rest_api_connection.get(uri, params)

    # get zone metadata
    def get_zone_metadata(self, zone_name):
        """Returns the metadata for the specified zone.

        Arguments:
        zone_name -- The name of the zone being returned.

        """
        return self.rest_api_connection.get("/v1/zones/" + zone_name)

    # delete a zone
    def delete_zone(self, zone_name):
        """Deletes the specified zone.

        Arguments:
        zone_name -- The name of the zone being deleted.

        """
        return self.rest_api_connection.delete("/v1/zones/"+zone_name)

    # RRSets
    # list rrsets for a zone
    def get_rrsets(self, zone_name, q=None, **kwargs):
        """Returns the list of RRSets in the specified zone.

        Arguments:
        zone_name -- The name of the zone.

        Keyword Arguments:
        q -- The search parameters, in a dict.  Valid keys are:
             ttl - must match the TTL for the rrset
             owner - substring match of the owner name
             value - substring match of the first BIND field value
        sort -- The sort column used to order the list. Valid values for the sort field are:
                OWNER
                TTL
                TYPE
        reverse -- Whether the list is ascending(False) or descending(True)
        offset -- The position in the list for the first returned element(0 based)
        limit -- The maximum number of rows to be returned.

        """
        uri = "/v1/zones/" + zone_name + "/rrsets"
        params = build_params(q, kwargs)
        return self.rest_api_connection.get(uri, params)

    # list rrsets by type for a zone
    # q	The query used to construct the list. Query operators are ttl, owner, and value
    def get_rrsets_by_type(self, zone_name, rtype, q=None, **kwargs):
        """Returns the list of RRSets in the specified zone of the specified type.

        Arguments:
        zone_name -- The name of the zone.
        rtype -- The type of the RRSets.  This can be numeric (1) or
                 if a well-known name is defined for the type (A), you can use it instead.

        Keyword Arguments:
        q -- The search parameters, in a dict.  Valid keys are:
             ttl - must match the TTL for the rrset
             owner - substring match of the owner name
             value - substring match of the first BIND field value
        sort -- The sort column used to order the list. Valid values for the sort field are:
                OWNER
                TTL
                TYPE
        reverse -- Whether the list is ascending(False) or descending(True)
        offset -- The position in the list for the first returned element(0 based)
        limit -- The maximum number of rows to be returned.

        """
        uri = "/v1/zones/" + zone_name + "/rrsets/" + rtype
        params = build_params(q, kwargs)
        return self.rest_api_connection.get(uri,params)

    # create an rrset
    def create_rrset(self, zone_name, rtype, owner_name, ttl, rdata):
        """Creates a new RRSet in the specified zone.

        Arguments:
        zone_name -- The zone that will contain the new RRSet.  The trailing dot is optional.
        rtype -- The type of the RRSet.  This can be numeric (1) or
                 if a well-known name is defined for the type (A), you can use it instead.
        owner_name -- The owner name for the RRSet.
                      If no trailing dot is supplied, the owner_name is assumed to be relative (foo).
                      If a trailing dot is supplied, the owner name is assumed to be absolute (foo.zonename.com.)
        ttl -- The TTL value for the RRSet.
        rdata -- The BIND data for the RRSet as a string.
                 If there is a single resource record in the RRSet, you can pass in the single string.
                 If there are multiple resource records  in this RRSet, pass in a list of strings.

        """
        if type(rdata) is not list:
            rdata = [rdata]
        rrset = {"ttl": ttl, "rdata": rdata}
        return self.rest_api_connection.post("/v1/zones/"+zone_name+"/rrsets/"+rtype+"/"+owner_name, json.dumps(rrset))

    # edit an rrset(PUT)
    def edit_rrset(self, zone_name, rtype, owner_name, ttl, rdata):
        """Updates an existing RRSet in the specified zone.

        Arguments:
        zone_name -- The zone that contains the RRSet.  The trailing dot is optional.
        rtype -- The type of the RRSet.  This can be numeric (1) or
                 if a well-known name is defined for the type (A), you can use it instead.
        owner_name -- The owner name for the RRSet.
                      If no trailing dot is supplied, the owner_name is assumed to be relative (foo).
                      If a trailing dot is supplied, the owner name is assumed to be absolute (foo.zonename.com.)
        ttl -- The updated TTL value for the RRSet.
        rdata -- The updated BIND data for the RRSet as a string.
                 If there is a single resource record in the RRSet, you can pass in the single string.
                 If there are multiple resource records  in this RRSet, pass in a list of strings.

        """
        if type(rdata) is not list:
            rdata = [rdata]
        rrset = {"ttl": ttl, "rdata": rdata}
        uri = "/v1/zones/" + zone_name + "/rrsets/" + rtype + "/" + owner_name + "/default"
        return self.rest_api_connection.put(uri,json.dumps(rrset))

    # delete an rrset
    def delete_rrset(self, zone_name, rtype, owner_name):
        """Deletes an RRSet.

        Arguments:
        zone_name -- The zone containing the RRSet to be deleted.  The trailing dot is optional.
        rtype -- The type of the RRSet.  This can be numeric (1) or
                 if a well-known name is defined for the type (A), you can use it instead.
        owner_name -- The owner name for the RRSet.
                      If no trailing dot is supplied, the owner_name is assumed to be relative (foo).
                      If a trailing dot is supplied, the owner name is assumed to be absolute (foo.zonename.com.)

        """
        return self.rest_api_connection.delete("/v1/zones/" + zone_name + "/rrsets/" + rtype + "/" + owner_name)

    # Accounts
    # get account details for user
    def get_account_details(self):
        """Returns a list of all accounts of which the current user is a member."""
        return self.rest_api_connection.get("/v1/accounts")

    # Version
    # get version
    def version(self):
        """Returns the version of the REST API server."""
        return self.rest_api_connection.get("/v1/version")

    # Status
    # get status
    def status(self):
        """Returns the status of the REST API server."""
        return self.rest_api_connection.get("/v1/status")


def build_params(q, args):
    params = {}
    params.update(args)
    if q is not None:
        params.update(q)
    return params
