__author__ = "UltraDNS"

import ultra_rest_client
import sys
import time

if len(sys.argv) != 5 and len(sys.argv) != 3:
    raise Exception("Expected use: python sample.py username password [use_http host:port]")

username = sys.argv[1]
password = sys.argv[2]
use_http = False
domain = "restapi.ultradns.com"

if len(sys.argv) == 5:
    use_http = sys.argv[3]
    domain = sys.argv[4]

c = ultra_rest_client.RestApiClient(username, password, "True" == use_http, domain)
print(f"version {c.version()}")
print(f"status {c.status()}")
account_details = c.get_account_details()
account_name = account_details['accounts'][0]['accountName']
print(f"account name {account_name}")
print(f"get zone metadata {c.get_zone_metadata_v3('mjoy-example.com.')}")
print(f"get first 5 primary zones with mjoy: {c.get_zones_v3(limit=5, sort='NAME', reverse=False, q={'name':'mjoy', 'zone_type':'PRIMARY'})}")
print("\n")
print(f"get first 5 secondary zones: {c.get_zones_v3(limit=5, sort='NAME', reverse=False, q={'zone_type':'SECONDARY'})}")
print("\n")
print(f"get all zones with 20 zones per page. First page is returned by default: {c.get_zones_v3(limit=20, q={'zone_status':'ALL'})}")
print("\n")
print(f"get next page of zones with 20 zones per page. Cursor returned by above request is used: {c.get_zones_v3(limit=20, cursor='MDAwMC10YW52aS1zaWduZWQuY29tLjpORVhU', q={'zone_status':'ALL'})}")
print(f"create primary zone result {c.create_primary_zone(account_name, 'foo.invalid.')}")
print(f"get zone metadata {c.get_zone_metadata('foo.invalid.')}")
print(f"delete zone {c.delete_zone('foo.invalid.')}")
all_zones = c.get_zones_v3()
print(all_zones)
first_zone_name = all_zones['zones'][0]['properties']['name']
print(f"zone name {first_zone_name}")
print(f"get_rrsets {c.get_rrsets(first_zone_name)}")
print(f"create_rrset {c.create_rrset(first_zone_name, 'A', 'foo', 300, '1.2.3.4')}")
print(f"get_rrsets {c.get_rrsets(first_zone_name)}")
print(f"get_rrsets_by_type {c.get_rrsets_by_type(first_zone_name, 'A')}")
print(f"edit_rrset {c.edit_rrset(first_zone_name, 'A', 'foo', 100, ['10.20.30.40'])}")
print(f"get_rrsets {c.get_rrsets(first_zone_name)}")
print(f"get_rrsets_by_type {c.get_rrsets_by_type(first_zone_name, 'A')}")
print(f"get_rrsets_by_type_owner {c.get_rrsets_by_type_owner(first_zone_name, 'A', 'foo')}")
print(f"delete_rrset {c.delete_rrset(first_zone_name, 'A', 'foo')}")
print(f"get_rrsets {c.get_rrsets(first_zone_name)}")
print(f"get_rrsets_by_type {c.get_rrsets_by_type(first_zone_name, 'A')}")
print(f"get_rrsets_by_type_owner {c.get_rrsets_by_type_owner(first_zone_name, 'A', 'foo')}")
print(f"batch delete {c.batch([{'method': 'DELETE', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo2'},{'method': 'DELETE', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo3'},])}")
print(f"get_rrsets_by_type {c.get_rrsets_by_type(first_zone_name, 'A')}")
print(f"get_rrsets_by_type_owner {c.get_rrsets_by_type_owner(first_zone_name, 'A', 'foo2')}")
print(f"batch create {c.batch([{'method': 'POST', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo2', 'body': {'ttl': 100, 'rdata': ['2.4.6.8']}},{'method': 'POST', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo3', 'body': {'ttl': 100, 'rdata': ['20.40.60.80']}},])}")
print(f"get_rrsets_by_type {c.get_rrsets_by_type(first_zone_name, 'A')}")
print(f"get_rrsets_by_type_owner {c.get_rrsets_by_type_owner(first_zone_name, 'A', 'foo2')}")
print(f"batch delete {c.batch([{'method': 'DELETE', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo2'},{'method': 'DELETE', 'uri': '/v1/zones/' + first_zone_name + '/rrsets/A/foo3'},])}")
print(f"get_rrsets_by_type {c.get_rrsets_by_type(first_zone_name, 'A')}")
print(f"get_rrsets_by_type_owner {c.get_rrsets_by_type_owner(first_zone_name, 'A', 'foo2')}")
print(f"get first 5 primary zones with j: {c.get_zones(offset=0, limit=5, sort='NAME', reverse=False, q={'name':'j', 'zone_type':'PRIMARY'})}")
result = c.create_primary_zone_by_upload(account_name, 'sample.client.me.', 'zone.txt')
print(f"create zone via upload: {result}")
while True:
    task_status = c.get_task(result['task_id'])
    print(f"task status: {c.get_task(result['task_id'])}")
    if task_status['code'] != "IN_PROCESS":
        break
    time.sleep(1)
print(f"all task status: {c.get_all_tasks()}")
print(f"delete task status: {c.clear_task(result['task_id'])}")
print(f"export zone: {c.export_zone('sample.client.me.')}")
print(f"delete zone: {c.delete_zone('sample.client.me.')}")