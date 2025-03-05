# Copyright 2024 - Vercara. All rights reserved.
# Vercara, the Vercara logo and related names and logos are registered
# trademarks, service marks or tradenames of Vercara. All other
# product names, company names, marks, logos and symbols may be trademarks
# of their respective owners.
__author__ = 'UltraDNS'

from ultra_rest_client import RestApiClient
import sys
import time
import os

if len(sys.argv) != 4 and len(sys.argv) != 1:
    raise Exception("Expected use: python sample.py [use_token use_http host:port]")

# Fetch credentials from environment variables
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
use_http = 'False'
use_token = 'False'
domain = 'api.ultradns.com'

# Check if credentials are available
if not username or not password:
    raise ValueError("Username and password must be set in environment variables.")

if len(sys.argv) == 4:
    use_token = sys.argv[1]
    use_http = sys.argv[2]
    domain = sys.argv[3]

test_zone_name='udns-python-rest-client-test.com.'

client = RestApiClient(username, password, 'True' == use_token, 'True' == use_http, domain)
print('version %s' % client.version())
print('status %s' % client.status())
account_details = client.get_account_details()
account_name = account_details['accounts'][0]['accountName']
print('account name %s' % account_name)
print('get zone metadata %s' % client.get_zone_metadata_v3("mjoy-example.com."))
print('sleeping for 20 mins')
print('get first 5 primary zones with mjoy: %s' % client.get_zones_v3(limit=5, sort="NAME", reverse=False, q={"name":"mjoy", "zone_type":"PRIMARY"}))
print('\n')
print('get first 5 secondary zones: %s' % client.get_zones_v3(limit=5, sort="NAME", reverse=False, q={"zone_type":"SECONDARY"}))
print('\n')
print('get all zones with 20 zones per page. First page is returned by default: %s' % client.get_zones_v3(limit=20, q={"zone_status":"ALL"}))
print('\n')
print('get next page of zones with 20 zones per page. Cursor returned by above request is used: %s' % client.get_zones_v3(limit=20, cursor='MDAwMC10YW52aS1zaWduZWQuY29tLjpORVhU', q={"zone_status":"ALL"}))
print('create primary zone result %s' % client.create_primary_zone(account_name, "foo.invalid."))
print('get zone metadata %s' % client.get_zone_metadata("foo.invalid."))
print('delete zone %s ' % client.delete_zone("foo.invalid."))
print('zone name %s ' % test_zone_name)
print('get_rrsets %s ' % client.get_rrsets(test_zone_name))
print('create_rrset %s ' % client.create_rrset(test_zone_name, "A", "foo", 300, "1.2.3.4"))
print('get_rrsets %s ' % client.get_rrsets(test_zone_name))
print('get_rrsets_by_type %s ' % client.get_rrsets_by_type(test_zone_name, "A"))
print('edit_rrset %s ' % client.edit_rrset(test_zone_name, "A", "foo", 100, ["10.20.30.40"]))
print('get_rrsets %s ' % client.get_rrsets(test_zone_name))
print('get_rrsets_by_type %s ' % client.get_rrsets_by_type(test_zone_name, "A"))
print('get_rrsets_by_type_owner %s ' % client.get_rrsets_by_type_owner(test_zone_name, "A", "foo"))
print('delete_rrset %s ' % client.delete_rrset(test_zone_name, "A", "foo"))
print('get_rrsets %s ' % client.get_rrsets(test_zone_name))
print('get_rrsets_by_type %s ' % client.get_rrsets_by_type(test_zone_name, "A"))
print('get_rrsets_by_type_owner %s ' % client.get_rrsets_by_type_owner(test_zone_name, "A", "foo"))
print('batch delete %s ' % client.batch([
    {'method': 'DELETE', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo2'},
    {'method': 'DELETE', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo3'},
]))

print('get_rrsets_by_type %s ' % client.get_rrsets_by_type(test_zone_name, "A"))
print('get_rrsets_by_type_owner %s ' % client.get_rrsets_by_type_owner(test_zone_name, "A", "foo2"))
print('batch create %s ' % client.batch([
    {'method': 'POST', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo2', 'body': {'ttl': 100, 'rdata': ['2.4.6.8']}},
    {'method': 'POST', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo3', 'body': {'ttl': 100, 'rdata': ['20.40.60.80']}},
]))
print('get_rrsets_by_type %s ' % client.get_rrsets_by_type(test_zone_name, "A"))
print('get_rrsets_by_type_owner %s ' % client.get_rrsets_by_type_owner(test_zone_name, "A", "foo2"))
print('batch delete %s ' % client.batch([
    {'method': 'DELETE', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo2'},
    {'method': 'DELETE', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo3'},
]))
print('get_rrsets_by_type %s ' % client.get_rrsets_by_type(test_zone_name, "A"))
print('get_rrsets_by_type_owner %s ' % client.get_rrsets_by_type_owner(test_zone_name, "A", "foo2"))

#getting zones with q, sort, offset, limit
print('get first 5 primary zones with j: %s' % client.get_zones(offset=0, limit=5, sort="NAME", reverse=False, q={"name":"j", "zone_type":"PRIMARY"}))

#creating a zone with upload
result = client.create_primary_zone_by_upload(account_name, 'sample.client.me.', '../zone.txt')
print('create zone via upload: %s' % result)

# check the task status
while True:
    task_status = client.get_task(result['task_id'])
    print('task status: %s ' % client.get_task(result['task_id']))
    if task_status['code'] != 'IN_PROCESS':
        break
    time.sleep(1)


#check all task status
print('all task status: %s ' % client.get_all_tasks())

#delete task status
print('delete task status: %s ' % client.clear_task(result['task_id']))

#export zonefile in bind format
print(('export zone: %s ' % client.export_zone('sample.client.me.')))

#delete the zone
print('delete zone: %s ' % client.delete_zone('sample.client.me.'))
