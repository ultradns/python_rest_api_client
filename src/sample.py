# Copyright 2000 - 2013 NeuStar, Inc.All rights reserved.
# NeuStar, the Neustar logo and related names and logos are registered
# trademarks, service marks or tradenames of NeuStar, Inc. All other
# product names, company names, marks, logos and symbols may be trademarks
# of their respective owners.
__author__ = 'Jon Bodner'

import ultra_rest_client
import sys

if len(sys.argv) != 5 and len(sys.argv) != 3:
    raise Exception("Expected use: python sample.py username password [use_http host:port]")

username = sys.argv[1]
password = sys.argv[2]
use_http = 'False'
domain = 'restapi.ultradns.com'

if len(sys.argv) == 5:
    use_http = sys.argv[3]
    domain = sys.argv[4]

c = ultra_rest_client.RestApiClient(username, password, 'True' == use_http, domain)
print c.version()
print c.status()
account_details = c.get_account_details()
account_name = account_details[u'accounts'][0][u'accountName']
print account_name
print c.create_primary_zone(account_name, "foo.invalid.")
print c.get_zone_metadata("foo.invalid.")
print c.delete_zone("foo.invalid.")
all_zones = c.get_zones_of_account(account_name, offset=0, limit=5, reverse=True)
first_zone_name = all_zones[u'zones'][0][u'properties'][u'name']
print first_zone_name
print c.get_rrsets(first_zone_name)
print c.create_rrset(first_zone_name, "A", "foo", 300, "1.2.3.4")
print c.get_rrsets(first_zone_name)
print c.get_rrsets_by_type(first_zone_name, "A")
print c.edit_rrset(first_zone_name, "A", "foo", 100, ["10.20.30.40"])
print c.get_rrsets(first_zone_name)
print c.get_rrsets_by_type(first_zone_name, "A")
print c.delete_rrset(first_zone_name, "A", "foo")
print c.get_rrsets(first_zone_name)
print c.get_rrsets_by_type(first_zone_name, "A")
