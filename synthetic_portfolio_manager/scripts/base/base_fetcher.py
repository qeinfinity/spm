import requests
import time
import logging
import hmac
import hashlib
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode

class BaseFetcher:
    def __init__(self, base_url: str, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 rate_limit: int = 1200):
        """Initialize base fetcher with API configuration
        
        Args:
            base_url: Base URL for API requests
            api_key: Optional API key for authenticated requests
            api_secret: Optional API secret for request signing
            rate_limit: Maximum requests per minute (default: 1200)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        
        # Rate limiting
        self.request_count = 0
        self.request_window_start = datetime.now()
        self.max_requests_per_minute = rate_limit
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _get_headers(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, str]:
        """Get headers for API request, including authentication if available"""
        headers = {
            'User-Agent': 'SPM/1.0',
            'Accept': 'application/json',
        }
        
        if self.api_key:
            headers['X-MBX-APIKEY'] = self.api_key
            
            # Add signature if api_secret is available
            if self.api_secret and params:
                query_string = urlencode(params)
                signature = hmac.new(
                    self.api_secret.encode('utf-8'),
                    query_string.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                params['signature'] = signature
                
        return headers
        
    def _check_rate_limit(self):
        """Implement rate limiting"""
        now = datetime.now()
        # Reset counter if window has passed
        if now - self.request_window_start > timedelta(minutes=1):
            self.request_count = 0
            self.request_window_start = now
            
        # Check if we're about to exceed rate limit
        if self.request_count >= self.max_requests_per_minute:
            sleep_time = 60 - (now - self.request_window_start).seconds
            if sleep_time > 0:
                self.logger.warning(f"Rate limit reached, sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
                self.request_count = 0
                self.request_window_start = datetime.now()
                
    def fetch_data(self, endpoint: str, params: Optional[Dict] = None, method: str = 'GET', 
                  authenticate: bool = False, retries: int = 3, retry_delay: int = 2) -> Optional[Any]:
        """Enhanced fetch_data method with better error handling and rate limiting
        
        Args:
            endpoint: API endpoint to call (without base URL)
            params: Query parameters
            method: HTTP method (GET/POST)
            authenticate: Whether to use API key authentication
            retries: Number of retries on failure
            retry_delay: Delay between retries in seconds
            
        Returns:
            Parsed JSON response or None on failure
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"  # Ensure clean URL joining
        headers = self._get_headers(endpoint, params) if authenticate else None
        
        for attempt in range(retries):
            try:
                self._check_rate_limit()
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params if method == 'GET' else None,
                    json=params if method == 'POST' else None,
                    timeout=30
                )
                
                self.request_count += 1
                
                # Log response status
                self.logger.debug(f"Request to {url} returned status {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                if self._validate_response(data):
                    return data
                else:
                    self.logger.error(f"Invalid response format from {url}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching data from {url}: {str(e)}. Attempt {attempt + 1}/{retries}")
                if attempt < retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error: {str(e)}")
                break
                
        return None
        
    def _validate_response(self, response: Dict) -> bool:
        """Validate API response format. Override this in specific implementations."""
        return bool(response)