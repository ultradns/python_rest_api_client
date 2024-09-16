import ultra_rest_client
import os
import time

username = os.environ.get('ULTRADNS_UNIT_TEST_USERNAME')
password = os.environ.get('ULTRADNS_UNIT_TEST_PASSWORD')
domain = os.environ.get('ULTRADNS_UNIT_TEST_HOST_URL')

test_zone_name='udns-python-rest-client-test.com.'

c = ultra_rest_client.RestApiClient(username, password, False, False, domain)
print(('version %s' % c.version()))
print(('status %s' % c.status()))
account_details = c.get_account_details()
account_name = account_details['accounts'][0]['accountName']
print(('account name %s' % account_name ))
print(('get zone metadata %s' % c.get_zone_metadata_v3(test_zone_name)))
print(('get first 5 primary zones with udns: %s' % c.get_zones_v3(limit=5, sort="NAME", reverse=False, q={"name":"udns", "zone_type":"PRIMARY"})))
print('\n')
print(('get first 5 secondary zones: %s' % c.get_zones_v3(limit=5, sort="NAME", reverse=False, q={"zone_type":"SECONDARY"})))
print('\n')
print(('get all zones with 25 zones per page. First page is returned by default: %s' % c.get_zones_v3(limit=25, q={"zone_status":"ALL"})))
print('\n')
print(('get next page of zones with 25 zones per page. Cursor returned by above request is used: %s' % c.get_zones_v3(limit=25, cursor='MTY1NDUxNTM4MTczMXNiLXN1YnBvb2wtY3J1ZC0xLmNvbS46TkVYVA==', q={"zone_status":"ALL"})))
print(('create primary zone result %s' % c.create_primary_zone(account_name, "foo.invalid.")))
print(('get zone metadata %s' % c.get_zone_metadata("foo.invalid.")))
print(('delete zone %s ' % c.delete_zone("foo.invalid.")))
print(('zone name %s ' % test_zone_name))
print(('get_rrsets %s ' % c.get_rrsets(test_zone_name)))
print(('create_rrset %s ' % c.create_rrset(test_zone_name, "A", "foo", 300, "1.2.3.4")))
print(('get_rrsets %s ' % c.get_rrsets(test_zone_name)))
print(('get_rrsets_by_type %s ' % c.get_rrsets_by_type(test_zone_name, "A")))
print(('edit_rrset %s ' % c.edit_rrset(test_zone_name, "A", "foo", 100, ["10.20.30.40"])))
print(('get_rrsets %s ' % c.get_rrsets(test_zone_name)))
print(('get_rrsets_by_type %s ' % c.get_rrsets_by_type(test_zone_name, "A")))
print(('get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(test_zone_name, "A", "foo")))
print(('delete_rrset %s ' % c.delete_rrset(test_zone_name, "A", "foo")))
print(('get_rrsets %s ' % c.get_rrsets(test_zone_name)))
print(('get_rrsets_by_type %s ' % c.get_rrsets_by_type(test_zone_name, "A")))
print(('get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(test_zone_name, "A", "foo")))
print(('batch delete %s ' % c.batch([
    {'method': 'DELETE', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo2'},
    {'method': 'DELETE', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo3'},
])))

print(('get_rrsets_by_type %s ' % c.get_rrsets_by_type(test_zone_name, "A")))
print(('get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(test_zone_name, "A", "foo2")))
print(('batch create %s ' % c.batch([
    {'method': 'POST', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo2', 'body': {'ttl': 100, 'rdata': ['2.4.6.8']}},
    {'method': 'POST', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo3', 'body': {'ttl': 100, 'rdata': ['20.40.60.80']}},
])))
print(('get_rrsets_by_type %s ' % c.get_rrsets_by_type(test_zone_name, "A")))
print(('get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(test_zone_name, "A", "foo2")))
print(('batch delete %s ' % c.batch([
    {'method': 'DELETE', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo2'},
    {'method': 'DELETE', 'uri': '/v1/zones/' + test_zone_name + '/rrsets/A/foo3'},
])))
print(('get_rrsets_by_type %s ' % c.get_rrsets_by_type(test_zone_name, "A")))
print(('get_rrsets_by_type_owner %s ' % c.get_rrsets_by_type_owner(test_zone_name, "A", "foo2")))

#getting zones with q, sort, offset, limit
print(('get first 5 primary zones with j: %s' % c.get_zones(offset=0, limit=5, sort="NAME", reverse=False, q={"name":"j", "zone_type":"PRIMARY"})))

#creating a zone with upload
result = c.create_primary_zone_by_upload(account_name, 'sample.client.me.', './zone.txt')
print(('create zone via upload: %s' % result))

# check the task status
while True:
    task_status = c.get_task(result['task_id'])
    print(('task status: %s ' % c.get_task(result['task_id'])))
    if task_status['code'] != 'IN_PROCESS':
        break
    time.sleep(1)


#check all task status
print(('all task status: %s ' % c.get_all_tasks()))

#delete task status
print(('delete task status: %s ' % c.clear_task(result['task_id'])))

#export zonefile in bind format
print(('export zone: %s ' % c.export_zone('sample.client.me.')))

#delete the zone
print(('delete zone: %s ' % c.delete_zone('sample.client.me.')))
