# Ultra REST Client Utilities

This directory contains utility classes for the Ultra REST Client.

## TaskHandler

The `TaskHandler` class is a utility for handling API responses that return a `task_id` or a `location`. It automatically polls the appropriate endpoint until the task is complete or an error occurs.

### How it works

1. When you create a `TaskHandler` instance with an API response, it inspects the response to determine if it contains a `task_id` or a `location`.
2. If a `task_id` is found, it polls the `/tasks/{task_id}` endpoint until the task is complete or an error occurs.
3. If a `location` is found, it polls the location URL until a final status is reached.
4. If neither a `task_id` nor a `location` is found, it returns the original response.

### Usage

```python
from ultra_rest_client import RestApiClient, TaskHandler

# Create a client
client = RestApiClient('username', 'password')

# Make an API call that returns a task_id
response = client.create_snapshot('example.com')

# Create a TaskHandler to handle the response
task_result = TaskHandler(response, client)

# The TaskHandler will poll until the task is complete
print(task_result)
```

### Parameters

- `response`: The API response to process.
- `client` (RestApiClient): The RestApiClient instance to use for API calls.
- `poll_interval` (int, optional): The interval in seconds between polling attempts. Defaults to 1.

## ReportHandler

The `ReportHandler` class is a utility for handling API responses from reporting API endpoints that return a `requestId`. It automatically polls the appropriate endpoint until the report is complete or an error occurs.

### How it works

1. When you create a `ReportHandler` instance with an API response, it inspects the response to determine if it contains a `requestId`.
2. If a `requestId` is found, it polls the appropriate endpoint until the report is complete or an error occurs.
3. If no `requestId` is found, it returns the original response.

### Usage

```python
from ultra_rest_client import RestApiClient, ReportHandler

# Create a client
client = RestApiClient('username', 'password')

# Make an API call that returns a requestId
response = client.create_advanced_nxdomain_report(
    startDate='2023-01-01',
    endDate='2023-01-31',
    zoneNames=['example.com']
)

# Create a ReportHandler to handle the response
# You can specify a maximum number of retries to avoid indefinite polling
report_result = ReportHandler(response, client, max_retries=30)

# The ReportHandler will poll until the report is complete
print(report_result)
```

### Parameters

- `response`: The API response to process.
- `client` (RestApiClient): The RestApiClient instance to use for API calls.
- `poll_interval` (int, optional): The interval in seconds between polling attempts. Defaults to 1.
- `max_retries` (int, optional): The maximum number of polling attempts. Defaults to None (unlimited). 