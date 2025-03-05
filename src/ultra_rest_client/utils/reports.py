"""
Report handling utilities for the Ultra REST Client.

This module provides utilities for handling report responses from the UltraDNS API.
"""
import time


class ReportHandler:
    """
    A utility class for handling API responses from reporting API endpoints.
    
    This class inspects an API response and, if it contains a requestId, polls
    the appropriate endpoint until the report is complete.
    """
    
    def __init__(self, response, client, poll_interval=1, max_retries=None):
        """
        Initialize the ReportHandler with an API response.
        
        Args:
            response: The API response to process.
            client (RestApiClient): The RestApiClient instance to use for API calls.
            poll_interval (int, optional): The interval in seconds between polling attempts.
                Defaults to 1.
            max_retries (int, optional): The maximum number of polling attempts.
                If None, will poll indefinitely until the report is complete.
                Defaults to None.
        
        Returns:
            The final result of the report polling, or the original response
            if no requestId is present.
        """
        self.client = client
        self.poll_interval = poll_interval
        self.max_retries = max_retries
        
        # Process the response
        self.result = self._process_response(response)
    
    def _process_response(self, response):
        """
        Process the API response and determine the appropriate action.
        
        Args:
            response: The API response to process.
            
        Returns:
            The final result after processing.
        """
        if isinstance(response, dict) and 'requestId' in response:
            return self._handle_report(response['requestId'])
        
        return response
    
    def _handle_report(self, request_id):
        """
        Handle a response containing a requestId.
        
        This method polls the report endpoint until the report is complete.
        
        Args:
            request_id (str): The ID of the report to poll.
            
        Returns:
            The final report result.
        """
        retry_count = 0
        
        while True:
            if self.max_retries is not None and retry_count >= self.max_retries:
                return {
                    'error': 'Maximum retry limit reached',
                    'requestId': request_id
                }
            
            report_response = self.client.get_report_results(request_id)
            
            if isinstance(report_response, dict):
                if 'errors' in report_response and isinstance(report_response['errors'], list):
                    for error in report_response['errors']:
                        if 'code' in error and str(error['code']) in ['410005', '410004']:
                            retry_count += 1
                            time.sleep(self.poll_interval)
                            break
                    else:
                        return report_response
                    
                    continue
                
                elif 'errorCode' in report_response:
                    error_code = str(report_response['errorCode'])
                    if error_code in ['410005', '410004']:
                        retry_count += 1
                        time.sleep(self.poll_interval)
                        continue
            
            return report_response
    
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