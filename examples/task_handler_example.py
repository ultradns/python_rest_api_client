#!/usr/bin/env python
"""
Example script demonstrating the use of the TaskHandler utility class.

This script shows how to use the TaskHandler to handle asynchronous task responses
from the UltraDNS API.
"""

from ultra_rest_client import RestApiClient, TaskHandler

# Initialize the client
client = RestApiClient('your_username', 'your_password')

# Example 1: Handling a response with a task_id
# --------------------------------------------
# Some API endpoints return a task_id indicating a background task
print("Example 1: Creating a snapshot (returns a task_id)")
response = client.create_snapshot('example.com')
print("Initial response:", response)

# The TaskHandler will automatically poll the task endpoint until completion
task_result = TaskHandler(response, client)
print("Final result after polling:")
print(task_result)  # This will print the final result

# Example 2: Handling a response with a location
# --------------------------------------------
# Some API endpoints return a location that needs to be polled until completion
print("\nExample 2: Creating a health check (returns a location)")
response = client.create_health_check('example.com')
print("Initial response:", response)

# The TaskHandler will automatically poll the location until completion
location_result = TaskHandler(response, client, poll_interval=2)  # Poll every 2 seconds
print("Final result after polling:")
print(location_result) 

# Example 3: Handling a regular response (no task_id or location)
# --------------------------------------------
# If no task_id or location is present, the TaskHandler will return the original response
print("\nExample 3: Getting zone information (returns a regular response)")
response = client.get_zone('example.com')
print("Initial response:", response)

regular_result = TaskHandler(response, client)
print("Result from TaskHandler:")
print(regular_result)  # This will print the original response