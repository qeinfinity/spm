import requests
import time

class BaseFetcher:
    def __init__(self, api_url, retries=3, delay=2):
        self.api_url = api_url
        self.retries = retries
        self.delay = delay

    def fetch_data(self, params=None):
        for attempt in range(self.retries):
            try:
                response = requests.get(self.api_url, params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching data: {e}. Retry {attempt+1}/{self.retries}")
                time.sleep(self.delay)
        return None