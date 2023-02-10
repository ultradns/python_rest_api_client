# Copyright 2000 - 2013 NeuStar, Inc.All rights reserved.
# NeuStar, the Neustar logo and related names and logos are registered
# trademarks, service marks or tradenames of NeuStar, Inc. All other
# product names, company names, marks, logos and symbols may be trademarks
# of their respective owners.
__author__ = 'Jon Bodner'

import ultra_rest_client
import sys
import time

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
print 'version %s' % c.version()
print 'status %s' % c.status()
account_details = c.get_account_details()
account_name = account_details[u'accounts'][0][u'accountName']
print 'account name %s' % account_name
print 'get zone metadata %s' % c.get_zone_metadata_v3("mjoy-example.com.")
print 'get first 5 primary zones with mjoy: %s' % c.get_zones_v3(limit=5, sort="NAME", reverse=False, q={"name":"mjoy", "zone_type":"PRIMARY"})
print '\n'
print 'get first 5 secondary zones: %s' % c.get_zones_v3(limit=5, sort="NAME", reverse=False, q={"zone_type":"SECONDARY"})
print '\n'
print 'get all zones with 20 zones per page. First page is returned by default: %s' % c.get_zones_v3(limit=20, q={"zone_status":"ALL"})
print '\n'
print 'get next page of zones with 20 zones per page. Cursor returned by above request is used: %s' % c.get_zones_v3(limit=20, cursor='MDAwMC10YW52aS1zaWduZWQuY29tLjpORVhU', q={"zone_status":"ALL"})
print 'create primary zone result %s' % c.create_primary_zone(account_name, "foo.invalid.")
print 'get zone metadata %s' % c.get_zone_metadata("foo.invalid.")
print 'delete zone %s ' % c.delete_zone("foo.invalid.")
all_zones = c.get_zones_of_account(account_name, offset=0, limit=5, reverse=True)
print all_zones
first_zone_name = all_zones[u'zones'][0][u'properties'][u'name']
print 'zone name %s ' % first_zone_name
print 'get_rrsets %s ' % c.get_rrsets(first_zone_name)
print 'create_rrset %s ' % c.create_rrset(first_zone_name, "A", "foo", 300, "1.2.3.4")
print 'get_rrsets %s ' % c.get_rrsets(first_zone_name)
print 'get_rrsets_by_type %s ' % c.get_rrsets_by_type(first_zone_name, "A")
print 'edit_rrset %s ' % c.edit_rrset(first_zone_name, "A", "foo", 100, ["10.20.30.40"])
print 'get_rrsets %s ' % c.get_rrsets(first_zone_name)
print 'get_rrsets_by_type %s ' % c.get_rrsets_by_type(first_zone_name, "A")
print 'get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(first_zone_name, "A", "foo")
print 'delete_rrset %s ' % c.delete_rrset(first_zone_name, "A", "foo")
print 'get_rrsets %s ' % c.get_rrsets(first_zone_name)
print 'get_rrsets_by_type %s ' % c.get_rrsets_by_type(first_zone_name, "A")
print 'get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(first_zone_name, "A", "foo")
print 'batch delete %s ' % c.batch([
    {'method': 'DELETE', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo2'},
    {'method': 'DELETE', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo3'},
])

print 'get_rrsets_by_type %s ' % c.get_rrsets_by_type(first_zone_name, "A")
print 'get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(first_zone_name, "A", "foo2")
print 'batch create %s ' % c.batch([
    {'method': 'POST', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo2', 'body': {'ttl': 100, 'rdata': ['2.4.6.8']}},
    {'method': 'POST', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo3', 'body': {'ttl': 100, 'rdata': ['20.40.60.80']}},
])
print 'get_rrsets_by_type %s ' % c.get_rrsets_by_type(first_zone_name, "A")
print 'get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(first_zone_name, "A", "foo2")
print 'batch delete %s ' % c.batch([
    {'method': 'DELETE', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo2'},
    {'method': 'DELETE', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo3'},
])
print 'get_rrsets_by_type %s ' % c.get_rrsets_by_type(first_zone_name, "A")
print 'get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(first_zone_name, "A", "foo2")

#getting zones with q, sort, offset, limit
print 'get first 5 primary zones with j: %s' % c.get_zones(offset=0, limit=5, sort="NAME", reverse=False, q={"name":"j", "zone_type":"PRIMARY"})

#creating a zone with upload
result = c.create_primary_zone_by_upload(account_name, 'sample.client.me.', '../zone.txt')
print 'create zone via upload: %s' % result

# check the task status
while True:
    task_status = c.get_task(result['task_id'])
    print 'task status: %s ' % c.get_task(result['task_id'])
    if task_status['code'] != 'IN_PROCESS':
        break
    time.sleep(1)


#check all task status
print 'all task status: %s ' % c.get_all_tasks()

#delete task status
print 'delete task status: %s ' % c.clear_task(result['task_id'])

#export zonefile in bind format
print('export zone: %s ' % c.export_zone('sample.client.me.'))

#delete the zone
print 'delete zone: %s ' % c.delete_zone('sample.client.me.')
