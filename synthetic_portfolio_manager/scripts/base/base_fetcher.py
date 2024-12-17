import time
import hmac
import hashlib
import requests
from typing import Dict, Optional, Any
from urllib.parse import urlencode
from datetime import datetime
from utilities.logging_config import get_logger

class BaseFetcher:
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None, rate_limit: int = 1200):
        """Initialize base fetcher with API configuration
        
        Args:
            base_url: Base URL for API endpoints
            api_key: Optional API key for authenticated endpoints
            api_secret: Optional API secret for signing requests
            rate_limit: Maximum requests per minute (default: 1200)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.last_request_time = 0
        self.logger = get_logger(self.__class__.__name__)
        
        # Set up session headers
        if self.api_key:
            self.session.headers.update({
                'X-MBX-APIKEY': self.api_key
            })
    
    def _add_signature(self, params: Dict) -> Dict:
        """Add HMAC SHA256 signature to request parameters
        
        Args:
            params: Request parameters to sign
            
        Returns:
            Dict with signature added
        """
        if not self.api_secret:
            return params
            
        # Add timestamp if not present
        if 'timestamp' not in params:
            params['timestamp'] = int(time.time() * 1000)
            
        # Create signature
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        return params
    
    def _wait_for_rate_limit(self):
        """Implement rate limiting by waiting if necessary"""
        if not self.rate_limit:
            return
            
        # Calculate minimum time between requests
        min_interval = 60.0 / self.rate_limit  # seconds per request
        
        # Wait if necessary
        elapsed = time.time() - self.last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
    
    def fetch_data(self, endpoint: str, params: Optional[Dict] = None,
                  method: str = 'GET', sign: bool = False,
                  retry_count: int = 3, retry_delay: float = 1.0) -> Optional[Any]:
        """Fetch data from API endpoint with rate limiting and retries
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            method: HTTP method (default: 'GET')
            sign: Whether to sign the request
            retry_count: Number of retries on failure
            retry_delay: Delay between retries in seconds
            
        Returns:
            Response data or None on error
        """
        params = params or {}
        endpoint = endpoint.lstrip('/')
        url = f"{self.base_url}/{endpoint}"
        
        # Add signature if required
        if sign:
            params = self._add_signature(params)
        
        for attempt in range(retry_count):
            try:
                # Rate limiting
                self._wait_for_rate_limit()
                
                # Make request
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params if method == 'GET' else None,
                    json=params if method != 'GET' else None
                )
                self.last_request_time = time.time()
                
                # Check for errors
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{retry_count}): {str(e)}"
                )
                
                # Break if it's our last attempt
                if attempt == retry_count - 1:
                    raise
                    
                # Wait before retrying
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                
        return None