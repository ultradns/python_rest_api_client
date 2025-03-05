#!/usr/bin/env python
"""
Example script demonstrating the use of the ReportHandler utility class.

This script shows how to use the ReportHandler to handle report generation API responses
from the UltraDNS API.
"""

from ultra_rest_client import RestApiClient, ReportHandler

# Initialize the client
client = RestApiClient('your_username', 'your_password')

# Example 1: Creating an advanced NXDOMAIN report
# --------------------------------------------
# The endpoint returns a requestId that needs to be polled until the report is complete
print("Example 1: Creating an advanced NXDOMAIN report")
response = client.create_advanced_nxdomain_report(
    startDate='2023-01-01',
    endDate='2023-01-31',
    zoneNames=['example.com']
)
print("Initial response:", response)

# The ReportHandler will automatically poll until the report is complete
report_result = ReportHandler(response, client)
print("Final result after polling:")
print(report_result)  # This will print the final result

# Example 2: Creating a projected query volume report
# --------------------------------------------
print("\nExample 2: Creating a projected query volume report")
response = client.create_projected_query_volume_report('your_account_name')
print("Initial response:", response)

# You can set a maximum number of retries to avoid indefinite polling
report_result = ReportHandler(response, client, max_retries=30)
print("Final result after polling (or max retries):")
print(report_result)