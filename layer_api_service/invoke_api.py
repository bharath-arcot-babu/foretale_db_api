"""
API Client for making HTTP requests.
"""

import requests
from typing import Dict, Any

class APIClient:
    def __init__(self):
        self.session = requests.Session()

    def post(self, url: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> requests.Response:
        """
        Make a POST request to the specified URL.
        
        Args:
            url (str): The URL to send the request to
            data (Dict[str, Any], optional): The data to send in the request body
            headers (Dict[str, str], optional): The headers to send with the request
            
        Returns:
            requests.Response: The response from the server
        """
        return self.session.post(url, json=data, headers=headers)

    def get(self, url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> requests.Response:
        """
        Make a GET request to the specified URL.
        
        Args:
            url (str): The URL to send the request to
            params (Dict[str, Any], optional): The query parameters to send with the request
            headers (Dict[str, str], optional): The headers to send with the request
            
        Returns:
            requests.Response: The response from the server
        """
        return self.session.get(url, params=params, headers=headers)
