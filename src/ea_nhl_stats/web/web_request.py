from typing import Any, Dict, List, Union
import logging
import requests

class WebRequest:
    """Handles HTTP requests to external APIs.
    
    This class provides a standardized way to make HTTP GET requests with proper
    error handling and logging.
    """
    
    def process(self, url: str) -> Union[Dict[str, Any], List[Any]]:
        """Makes an HTTP GET request to the specified URL.
        
        Args:
            url: The URL to make the request to.
            
        Returns:
            The JSON response from the API parsed into a Python object.
            
        Raises:
            requests.exceptions.RequestException: If the HTTP request fails.
        """
        logging.debug(f"Making API call to URL: {url}")
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MyTestClient/1.0)"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            logging.debug(f"API Response Status Code: {response.status_code}")
            logging.debug(f"API Response Content: {response.text}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            raise 