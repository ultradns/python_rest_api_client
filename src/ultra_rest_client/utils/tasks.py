"""
Task handling utilities for the Ultra REST Client.

This module provides utilities for handling asynchronous tasks and location-based responses
from the UltraDNS API.
"""
import time


class TaskHandler:
    """
    A utility class for handling API responses that return a task_id or location.
    
    This class inspects an API response and, based on its contents, either polls a task endpoint
    or a location endpoint until a final result is reached.
    """
    
    def __init__(self, response, client, poll_interval=1):
        """
        Initialize the TaskHandler with an API response.
        
        Args:
            response: The API response to process.
            client (RestApiClient): The RestApiClient instance to use for API calls.
            poll_interval (int, optional): The interval in seconds between polling attempts.
                Defaults to 1.
        
        Returns:
            The final result of the task or location polling, or the original response
            if neither a task_id nor a location is present.
        """
        self.poll_interval = poll_interval
        self.client = client
        
        self.result = self._process_response(response)
    
    def _process_response(self, response):
        """
        Process the API response and determine the appropriate action.
        
        Args:
            response: The API response to process.
            
        Returns:
            The final result after processing.
        """
        if isinstance(response, dict) and 'task_id' in response:
            return self._handle_task(response['task_id'])
        
        if isinstance(response, dict) and 'location' in response:
            return self._handle_location(response['location'])
        
        return response
    
    def _handle_task(self, task_id):
        """
        Handle a response containing a task_id.
        
        This method polls the /tasks/{task_id} endpoint until the task is complete
        or an error occurs.
        
        Args:
            task_id (str): The ID of the task to poll.
            
        Returns:
            The final result of the task.
        """
        while True:
            task_response = self.client.get_task(task_id)
            
            if task_response.get('code') in ['PENDING', 'IN_PROCESS']:
                time.sleep(self.poll_interval)
                continue
            
            if task_response.get('code') == 'ERROR':
                return task_response
            
            if task_response.get('code') == 'COMPLETE':
                if task_response.get('hasData', False):
                    result_uri = task_response.get('resultUri')
                    if result_uri:
                        return self.client.rest_api_connection.get(result_uri)
                
                return task_response
            
            return task_response
    
    def _handle_location(self, location):
        """
        Handle a response containing a location.
        
        This method polls the location URL until a final status is reached.
        
        Args:
            location (str): The location URL to poll.
            
        Returns:
            The final result from the location.
        """
        while True:
            location_response = self.client.rest_api_connection.get(location)
            
            state = location_response.get('state', '').upper()
            status = location_response.get('status', '').upper()
            
            if state in ['COMPLETED', 'ERROR'] or status in ['COMPLETED', 'ERROR']:
                return location_response
            
            time.sleep(self.poll_interval)
    
    def __repr__(self):
        """Return a string representation of the result."""
        return repr(self.result)
    
    def __str__(self):
        """Return a string representation of the result."""
        return str(self.result)
    
    def __getitem__(self, key):
        """Allow dictionary-like access to the result."""
        return self.result[key]
    
    def __iter__(self):
        """Allow iteration over the result."""
        return iter(self.result)
    
    def __len__(self):
        """Return the length of the result."""
        return len(self.result)
    
    def get(self, key, default=None):
        """Get a value from the result with a default if the key is not found."""
        if isinstance(self.result, dict):
            return self.result.get(key, default)
        return default 