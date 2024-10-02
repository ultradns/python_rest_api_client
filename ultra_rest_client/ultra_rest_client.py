# Copyright 2023 Vercara. All rights reserved.
# Vercara, the Vercara logo and related names and logos are registered
# trademarks, service marks or tradenames of Vercara. All other
# product names, company names, marks, logos and symbols may be trademarks
# of their respective owners.
__author__ = 'UltraDNS'
from .connection import RestApiConnection
import json
import time

class RestApiClient:
    def __init__(self, bu: str, pr: str = None, use_token: bool = False, use_http: bool =False, host: str = "api.ultradns.com"):
        """Initialize a Rest API Client.

        Arguments:
        bu (str) -- Either username or bearer token based on `use_token` flag.
        pr (str, optional) -- Either password or refresh token based on `use_token` flag. Defaults to None.
        use_token (bool, optional) -- If True, treats `bu` as bearer token and `pr` as refresh token. Defaults to False.

        Keyword Arguments:
        use_http (bool, optional) -- For internal testing purposes only, lets developers use http instead of https.
        host (str) -- Allows you to point to a server other than the production server.

        Raises:
        ValueError -- If `pr` is not provided when `use_token` is True.
        """

        if use_token:
            self.access_token = bu
            self.refresh_token = pr
            self.rest_api_connection = RestApiConnection(use_http, host, bu, pr)
            if not self.refresh_token:
                print(
                    "Warning: Passing a Bearer token with no refresh token means the client state will expire after an hour.")
        else:
            if not pr:
                raise ValueError("Password is required when providing a username.")
            self.rest_api_connection = RestApiConnection(use_http, host)
            self.rest_api_connection.auth(bu, pr)

    # Zones
    # create a primary zone
    def create_primary_zone(self, account_name, zone_name):
        """Creates a new primary zone.

        Arguments:
        account_name -- The name of the account that will contain this zone.
        zone_name -- The name of the zone.  It must be unique.

        """
        zone_data = {
            "properties": {
                "name": zone_name,
                "accountName": account_name,
                "type": "PRIMARY"
            },
            "primaryCreateInfo": {
                "forceImport": True,
                "createType": "NEW"
            }
        }
        return self.rest_api_connection.post("/v1/zones", json.dumps(zone_data))

    # create primary zone by file upload
    def create_primary_zone_by_upload(self, account_name, zone_name, bind_file):
        """Creates a new primary zone by uploading a bind file

        Arguments:
        account_name -- The name of the account that will contain this zone.
        zone_name -- The name of the zone.  It must be unique.
        bind_file -- The file to upload.

        """
        zone_data = {
            "properties": {
                "name": zone_name,
                "accountName": account_name,
                "type": "PRIMARY"
            },
            "primaryCreateInfo": {
                "forceImport": True,
                "createType": "UPLOAD"
            }
        }
        files = {
            'zone': ('', json.dumps(zone_data), 'application/json'),
            'file': ('file', open(bind_file, 'rb'), 'application/octet-stream')
        }
        return self.rest_api_connection.post_multi_part("/v1/zones", files)

    # create a primary zone using axfr
    def create_primary_zone_by_axfr(self, account_name, zone_name, master, tsig_key=None, key_value=None):
        """Creates a new primary zone by zone transferring off a master.

        Arguments:
        account_name -- The name of the account that will contain this zone.
        zone_name -- The name of the zone.  It must be unique.
        master -- Primary name server IP address.

        Keyword Arguments:
        tsig_key -- For TSIG-enabled zones: The transaction signature key.
                    NOTE: Requires key_value.
        key_value -- TSIG key secret.

        """
        zone_properties = {
            "name": zone_name,
            "accountName": account_name,
            "type": "PRIMARY"
        }
        name_server_info = {"ip": master}
        if tsig_key and key_value:
            name_server_info.update({"tsigKey": tsig_key, "tsigKeyValue": key_value})

        primary_zone_info = {
            "forceImport": True,
            "createType": "TRANSFER",
            "nameServer": name_server_info
        }
        zone_data = {
            "properties": zone_properties,
            "primaryCreateInfo": primary_zone_info
        }
        return self.rest_api_connection.post("/v1/zones", json.dumps(zone_data))

    # create a secondary zone
    def create_secondary_zone(self, account_name, zone_name, master, tsig_key=None, key_value=None):
        """Creates a new secondary zone.

        Arguments:
        account_name -- The name of the account.
        zone_name -- The name of the zone.
        master -- Primary name server IP address.

        Keyword Arguments:
        tsig_key -- For TSIG-enabled zones: The transaction signature key.
                    NOTE: Requires key_value.
        key_value -- TSIG key secret.

        """
        zone_properties = {
            "name": zone_name,
            "accountName": account_name,
            "type": "SECONDARY"
        }
        name_server_info = {"ip": master}
        if tsig_key and key_value:
            name_server_info.update({"tsigKey": tsig_key, "tsigKeyValue": key_value})

        name_server_ip_list = {
            "nameServerIpList": {
                "nameServerIp1": name_server_info
            }
        }
        secondary_zone_info = {
            "primaryNameServers": name_server_ip_list
        }
        zone_data = {
            "properties": zone_properties,
            "secondaryCreateInfo": secondary_zone_info
        }
        return self.rest_api_connection.post("/v1/zones", json.dumps(zone_data))

    # force zone axfr
    def force_axfr(self, zone_name):
        """Force a secondary zone transfer.

        Arguments:
        zone_name -- The zone name.  The trailing dot is optional.

        """
        return self.rest_api_connection.post(f"/v1/zones/{zone_name}/transfer")

    # convert secondary
    def convert_zone(self, zone_name):
        """Convert a secondary zone to primary. This cannot be reversed.

        Arguments:
        zone_name -- The zone name. The trailing dot is optional.

        """
        return self.rest_api_connection.post(f"/v1/zones/{zone_name}/convert")

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
        uri = f"/v1/accounts/{account_name}/zones"
        params = build_params(q, kwargs)
        return self.rest_api_connection.get(uri, params)

    # list zones for all user accounts
    def get_zones(self, q=None, **kwargs):
        """Returns a list of zones across all of the user's accounts.

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
        uri = "/v1/zones"
        params = build_params(q, kwargs)
        return self.rest_api_connection.get(uri, params)

    # list zones for all user accounts using v3 url
    def get_zones_v3(self, q=None, **kwargs):
        """Returns a list of zones across all of the user's accounts.

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
        limit -- The maximum number of rows to be returned.

        """
        uri = "/v3/zones"
        params = build_params(q, kwargs)
        return self.rest_api_connection.get(uri, params)

    # get zone metadata
    def get_zone_metadata(self, zone_name):
        """Returns the metadata for the specified zone.

        Arguments:
        zone_name -- The name of the zone being returned.

        """
        return self.rest_api_connection.get(f"/v1/zones/{zone_name}")

    # get zone metadata v3
    def get_zone_metadata_v3(self, zone_name):
        """Returns the metadata for the specified zone.

        Arguments:
        zone_name -- The name of the zone being returned.

        """
        return self.rest_api_connection.get(f"/v3/zones/{zone_name}")

    # delete a zone
    def delete_zone(self, zone_name):
        """Deletes the specified zone.

        Arguments:
        zone_name -- The name of the zone being deleted.

        """
        return self.rest_api_connection.delete(f"/v1/zones/{zone_name}")


    # update secondary zone name servers (PATCH)
    def edit_secondary_name_server(self, zone_name, primary=None, backup=None, second_backup=None):
        """Edit the axfr name servers of a secondary zone.

        Arguments:
        zone_name -- The name of the secondary zone being edited.
        primary -- The primary name server value.

        Keyword Arguments:
        backup -- The backup name server if any.
        second_backup -- The second backup name server.

        """
        name_server_info = {
            f'nameServerIp{i+1}': {'ip': ip} for i, ip in enumerate([primary, backup, second_backup]) if ip is not None
        }
        zone_data = {
            "secondaryCreateInfo": {
                "primaryNameServers": {
                    "nameServerIpList": name_server_info
                }
            }
        }
        return self.rest_api_connection.patch(f"/v1/zones/{zone_name}", json.dumps(zone_data))

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
        uri = f"/v1/zones/{zone_name}/rrsets"
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
        uri = f"/v1/zones/{zone_name}/rrsets/{rtype}"
        params = build_params(q, kwargs)
        return self.rest_api_connection.get(uri, params)

    # list rrsets by type and owner for a zone
    # q	The query used to construct the list. Query operators are ttl, owner, and value
    def get_rrsets_by_type_owner(self, zone_name, rtype, owner_name, q=None, **kwargs):
        """Returns the list of RRSets in the specified zone of the specified type.

        Arguments:
        zone_name -- The name of the zone.
        rtype -- The type of the RRSets.  This can be numeric (1) or
                 if a well-known name is defined for the type (A), you can use it instead.
        owner_name -- The owner name for the RRSet.
                      If no trailing dot is supplied, the owner_name is assumed to be relative (foo).
                      If a trailing dot is supplied, the owner name is assumed to be absolute (foo.zonename.com.)

        Keyword Arguments:
        q -- The search parameters, in a dict.  Valid keys are:
             ttl - must match the TTL for the rrset
             value - substring match of the first BIND field value
        sort -- The sort column used to order the list. Valid values for the sort field are:
                TTL
                TYPE
        reverse -- Whether the list is ascending(False) or descending(True)
        offset -- The position in the list for the first returned element(0 based)
        limit -- The maximum number of rows to be returned.

        """
        uri = f"/v1/zones/{zone_name}/rrsets/{rtype}/{owner_name}"
        params = build_params(q, kwargs)
        return self.rest_api_connection.get(uri, params)

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
        if not isinstance(rdata, list):
            rdata = [rdata]
        rrset = {"ttl": ttl, "rdata": rdata}
        return self.rest_api_connection.post(f"/v1/zones/{zone_name}/rrsets/{rtype}/{owner_name}", json.dumps(rrset))

    # edit an rrset (PUT)
    def edit_rrset(self, zone_name, rtype, owner_name, ttl, rdata, profile=None):
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
        profile -- The profile info if this is updating a resource pool

        """
        if not isinstance(rdata, list):
            rdata = [rdata]
        rrset = {"ttl": ttl, "rdata": rdata}
        if profile:
            rrset["profile"] = profile
        uri = f"/v1/zones/{zone_name}/rrsets/{rtype}/{owner_name}"
        return self.rest_api_connection.put(uri, json.dumps(rrset))

    # edit an rrset's rdata (PATCH)
    def edit_rrset_rdata(self, zone_name, rtype, owner_name, rdata, profile=None):
        """Updates an existing RRSet's Rdata in the specified zone.

        Arguments:
        zone_name -- The zone that contains the RRSet.  The trailing dot is optional.
        rtype -- The type of the RRSet.  This can be numeric (1) or
                 if a well-known name is defined for the type (A), you can use it instead.
        owner_name -- The owner name for the RRSet.
                      If no trailing dot is supplied, the owner_name is assumed to be relative (foo).
                      If a trailing dot is supplied, the owner name is assumed to be absolute (foo.zonename.com.)
        rdata -- The updated BIND data for the RRSet as a string.
                 If there is a single resource record in the RRSet, you can pass in the single string.
                 If there are multiple resource records  in this RRSet, pass in a list of strings.
        profile -- The profile info if this is updating a resource pool

        """
        if not isinstance(rdata, list):
            rdata = [rdata]
        rrset = {"rdata": rdata}
        method = "patch"
        if profile:
            rrset["profile"] = profile
            method = "put"
        uri = f"/v1/zones/{zone_name}/rrsets/{rtype}/{owner_name}"
        return getattr(self.rest_api_connection, method)(uri,json.dumps(rrset))

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
        return self.rest_api_connection.delete(f"/v1/zones/{zone_name}/rrsets/{rtype}/{owner_name}")

    # Web Forwards
    # get web forwards
    def get_web_forwards(self, zone_name):
        """Return all web forwards for a specific zone.

        Arguments:
        zone_name -- The zone for which to return a list of current web forwards. The response will include
                             the system-generated guid for each object.

        """
        return self.rest_api_connection.get(f"/v1/zones/{zone_name}/webforwards")

    # create web forward
    def create_web_forward(self, zone_name, request_to, redirect_to, forward_type):
        """Create a web forward record.

        Arguments:
        zone_name -- The zone in which the web forward is to be created.
        request_to -- The URL to be redirected. You may use http:// and ftp://.
        forward_type -- The type of forward. Valid options include:
                                   Framed
                                   HTTP_301_REDIRECT
                                   HTTP_302_REDIRECT
                                   HTTP_303_REDIRECT
                                   HTTP_307_REDIRECT

        """
        web_forward = {
            "requestTo": request_to,
            "defaultRedirectTo": redirect_to,
            "defaultForwardType": forward_type
        }
        uri = f"/v1/zones/{zone_name}/webforwards"
        return self.rest_api_connection.post(uri, json.dumps(web_forward))

    # delete web forward
    def delete_web_forward(self, zone_name, guid):
        """Return all web forwards for a specific zone.

        Arguments:
        zone_name -- The zone containing the web forward to be deleted.
        guid -- The system-generated unique id for the web forward.

        """
        return self.rest_api_connection.delete(f"/v1/zones/{zone_name}/webforwards/{guid}")

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

    # Tasks
    def get_all_tasks(self):
        return self.rest_api_connection.get("/v1/tasks")

    def get_task(self, task_id):
        return self.rest_api_connection.get(f"/v1/tasks/{task_id}")

    def clear_task(self, task_id):
        return self.rest_api_connection.delete(f"/v1/tasks/{task_id}")

    # Batch
    def batch(self, batch_list):
        """Sends multiple requests as a single transaction.

        Arguments:
        batch_list -- a list of request objects.
            Each request must have:
            method -- valid values are POST, PATCH, PUT, GET, DELETE
            uri -- The path for the request
            If the request should have a body, there is a third field:
            body (only if required) - The body of the request
        """
        return self.rest_api_connection.post("/v1/batch", json.dumps(batch_list))

    # Create an SB Pool
    # Sample JSON for an SB pool -- see the REST API docs for their descriptions
    # {
    # "ttl": 120,
    #     "rdata": [
    #         "4.5.6.7", "199.7.167.22", "1.2.3.4", "5.6.7.8"
    #     ],
    #     "profile": {
    #         "@context": "http://schemas.ultradns.com/SBPool.jsonschema",
    #         "description": "description",
    #         "runProbes": true,
    #         "actOnProbes": true,
    #         "order": "ROUND_ROBIN",
    #         "maxActive": 1,
    #         "maxServed": 0,
    #         "rdataInfo": [
    #             {
    #                 "state": "ACTIVE",
    #                 "runProbes": true,
    #                 "priority": 2,
    #                 "failoverDelay": 0,
    #                 "threshold": 1
    #             },
    #             {
    #                 "state": "INACTIVE",
    #                 "runProbes": true,
    #                 "priority": 1,
    #                 "failoverDelay": 0,
    #                 "threshold": 1
    #             },
    #             {
    #                 "state": "ACTIVE",
    #                 "runProbes": true,
    #                 "priority": 1,
    #                 "failoverDelay": 1,
    #                 "threshold": 1
    #             },
    #             {
    #                 "state": "INACTIVE",
    #                 "runProbes": true,
    #                 "priority": 2,
    #                 "failoverDelay": 3,
    #                 "threshold": 1
    #             }
    #         ],
    #         "backupRecords": [
    #             {
    #                 "rdata":"1.2.2.2",
    #                 "failoverDelay": 1
    #             }
    #         ]
    #     }
    # }

    def _build_sb_rrset(self, backup_record_list, pool_info, rdata_info, ttl):
        rdata = list(rdata_info.keys())
        rdata_info_list = list(rdata_info.values())

        profile = {
            "@context": "http://schemas.ultradns.com/SBPool.jsonschema",
            "backupRecords": backup_record_list,
            "rdataInfo": rdata_info_list
        }
        for p in pool_info:
            profile[p] = pool_info[p]
        rrset = {
            "ttl": ttl,
            "rdata": rdata,
            "profile": profile
        }
        return rrset

    def create_sb_pool(self, zone_name, owner_name, ttl, pool_info, rdata_info, backup_record_list):
        """Creates a new SB Pool.

        Arguments:
        zone_name -- The zone that contains the RRSet.  The trailing dot is optional.
        owner_name -- The owner name for the RRSet.
                      If no trailing dot is supplied, the owner_name is assumed to be relative (foo).
                      If a trailing dot is supplied, the owner name is assumed to be absolute (foo.zonename.com.)
        ttl -- The updated TTL value for the RRSet.
        pool_info -- dict of information about the pool
        rdata_info -- dict of information about the records in the pool.
                      The keys in the dict are the A and CNAME records that make up the pool.
                      The values are the rdataInfo for each of the records
        backup_record_list -- list of dicts of information about the backup (all-fail) records in the pool.
                        There are two key/value in each dict:
                            rdata - the A or CNAME for the backup record
                            failoverDelay - the time to wait to fail over (optional, defaults to 0)
        """
        rrset = self._build_sb_rrset(backup_record_list, pool_info, rdata_info, ttl)
        endpoint = f"/v1/zones/{zone_name}/rrsets/A/{owner_name}"
        return self.rest_api_connection.post(endpoint, json=rrset)

    # Update an SB Pool
    def edit_sb_pool(self, zone_name, owner_name, ttl, pool_info, rdata_info, backup_record_list):
        """Updates an existing SB Pool in the specified zone.
        :param zone_name: The zone that contains the RRSet.  The trailing dot is optional.
        :param owner_name: The owner name for the RRSet.
                      If no trailing dot is supplied, the owner_name is assumed to be relative (foo).
                      If a trailing dot is supplied, the owner name is assumed to be absolute (foo.zonename.com.)
        :param ttl: The updated TTL value for the RRSet.
        :param pool_info: dict of information about the pool
        :param rdata_info: dict of information about the records in the pool.
                      The keys in the dict are the A and CNAME records that make up the pool.
                      The values are the rdataInfo for each of the records
        :param backup_record_list: list of dicts of information about the backup (all-fail) records in the pool.
                        There are two key/value in each dict:
                            rdata - the A or CNAME for the backup record
                            failoverDelay - the time to wait to fail over (optional, defaults to 0)
        """
        rrset = self._build_sb_rrset(backup_record_list, pool_info, rdata_info, ttl)
        endpoint = f"/v1/zones/{zone_name}/rrsets/A/{owner_name}"
        return self.rest_api_connection.put(endpoint, json=rrset)

    def _build_tc_rrset(self, backup_record, pool_info, rdata_info, ttl):
        rdata = list(rdata_info.keys())
        rdata_info_list = list(rdata_info.values())

        profile = {
            "@context": "http://schemas.ultradns.com/TCPool.jsonschema",
            "backupRecord": backup_record,
            "rdataInfo": rdata_info_list
        }
        for p in pool_info:
            profile[p] = pool_info[p]
        rrset = {
            "ttl": ttl,
            "rdata": rdata,
            "profile": profile
        }
        return rrset

    # Create a TC Pool
    # Sample JSON for a TC pool -- see the REST API docs for their descriptions
    # {
    # "ttl": 120,
    #     "rdata": [
    #         "4.5.6.7", "199.7.167.22", "1.2.3.4", "5.6.7.8"
    #     ],
    #     "profile": {
    #         "@context": "http://schemas.ultradns.com/TCPool.jsonschema",
    #         "description": "description",
    #         "runProbes": true,
    #         "actOnProbes": true,
    #         "maxToLB": 1,
    #         "rdataInfo": [
    #             {
    #                 "state": "ACTIVE",
    #                 "runProbes": true,
    #                 "priority": 2,
    #                 "failoverDelay": 0,
    #                 "threshold": 1,
    #                 "weight": 2
    #             },
    #             {
    #                 "state": "INACTIVE",
    #                 "runProbes": true,
    #                 "priority": 1,
    #                 "failoverDelay": 0,
    #                 "threshold": 1,
    #                 "weight": 2
    #             },
    #             {
    #                 "state": "ACTIVE",
    #                 "runProbes": true,
    #                 "priority": 1,
    #                 "failoverDelay": 1,
    #                 "threshold": 1,
    #                 "weight": 4
    #             },
    #             {
    #                 "state": "INACTIVE",
    #                 "runProbes": true,
    #                 "priority": 2,
    #                 "failoverDelay": 3,
    #                 "threshold": 1,
    #                 "weight": 8
    #             }
    #         ],
    #         "backupRecord": {
    #                 "rdata":"1.2.2.2",
    #                 "failoverDelay": 1
    #         }
    #     }
    # }
    def create_tc_pool(self, zone_name, owner_name, ttl, pool_info, rdata_info, backup_record):
        """Creates a new TC Pool.

        Arguments:
        zone_name -- The zone that contains the RRSet.  The trailing dot is optional.
        owner_name -- The owner name for the RRSet.
                      If no trailing dot is supplied, the owner_name is assumed to be relative (foo).
                      If a trailing dot is supplied, the owner name is assumed to be absolute (foo.zonename.com.)
        ttl -- The updated TTL value for the RRSet.
        pool_info -- dict of information about the pool
        rdata_info -- dict of information about the records in the pool.
                      The keys in the dict are the A and CNAME records that make up the pool.
                      The values are the rdataInfo for each of the records
        backup_record -- dict of information about the backup (all-fail) records in the pool.
                        There are two key/value in the dict:
                            rdata - the A or CNAME for the backup record
                            failoverDelay - the time to wait to fail over (optional, defaults to 0)
        """

        rrset = self._build_tc_rrset(backup_record, pool_info, rdata_info, ttl)
        endpoint = f"/v1/zones/{zone_name}/rrsets/A/{owner_name}"
        return self.rest_api_connection.post(endpoint, json=rrset)

    # Update an SB Pool
    def edit_tc_pool(self, zone_name, owner_name, ttl, pool_info, rdata_info, backup_record):
        """Updates an existing TC Pool in the specified zone.
        :param zone_name: The zone that contains the RRSet.  The trailing dot is optional.
        :param owner_name: The owner name for the RRSet.
                      If no trailing dot is supplied, the owner_name is assumed to be relative (foo).
                      If a trailing dot is supplied, the owner name is assumed to be absolute (foo.zonename.com.)
        :param ttl: The updated TTL value for the RRSet.
        :param pool_info: dict of information about the pool
        :param rdata_info: dict of information about the records in the pool.
                      The keys in the dict are the A and CNAME records that make up the pool.
                      The values are the rdataInfo for each of the records
        :param backup_record: dict of information about the backup (all-fail) records in the pool.
                        There are two key/value in the dict:
                            rdata - the A or CNAME for the backup record
                            failoverDelay - the time to wait to fail over (optional, defaults to 0)
        """
        rrset = self._build_tc_rrset(backup_record, pool_info, rdata_info, ttl)
        endpoint = f"/v1/zones/{zone_name}/rrsets/A/{owner_name}"
        return self.rest_api_connection.put(endpoint, json=rrset)

    # export zone in bind format
    def export_zone(self, zone_name):
        """Returns a zone file in bind format
    
        Arguments:
        zone_name -- The name of the zone being returned. A single zone as a string.
    
        """
        zonejson = json.dumps({'zoneNames': [zone_name]})
        status = self.rest_api_connection.post("/v3/zones/export", json=zonejson)
        task_id = status.get('task_id')

        while True:
            task_status = self.rest_api_connection.get(f"/v1/tasks/{task_id}")
            if task_status['code'] != 'IN_PROCESS':
                break
            time.sleep(1)

        result = self.rest_api_connection.get(f"/v1/tasks/{task_id}/result")
        self.clear_task(task_id)
        return result

def build_params(q, args):
    params = args.copy()
    if q:
        params['q'] = ' '.join(f"{k}:{v}" for k, v in q.items())
    return params
