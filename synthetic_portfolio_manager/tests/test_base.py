"""Tests for base classes."""

import unittest
from scripts.base.base_fetcher import BaseFetcher
from scripts.base.base_scraper import BaseScraper
from scripts.base.base_cache import BaseCache

class TestBaseFetcher(unittest.TestCase):
    def test_fetch_data(self):
        fetcher = BaseFetcher("https://api.binance.com/api/v3/ticker/price")
        result = fetcher.fetch_data(params={"symbol": "BTCUSDT"})
        self.assertIn("symbol", result)

def test_base_scraper():
    """Test BaseScraper abstract methods."""
    with pytest.raises(TypeError):
        BaseScraper()

def test_base_cache():
    """Test BaseCache abstract methods."""
    with pytest.raises(TypeError):
        BaseCache()

if __name__ == "__main__":
    unittest.main()