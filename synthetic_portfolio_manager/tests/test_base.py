"""Tests for base classes."""

import pytest
from scripts.base.base_fetcher import BaseFetcher
from scripts.base.base_scraper import BaseScraper
from scripts.base.base_cache import BaseCache

def test_base_fetcher():
    """Test BaseFetcher abstract methods."""
    with pytest.raises(TypeError):
        BaseFetcher()

def test_base_scraper():
    """Test BaseScraper abstract methods."""
    with pytest.raises(TypeError):
        BaseScraper()

def test_base_cache():
    """Test BaseCache abstract methods."""
    with pytest.raises(TypeError):
        BaseCache()
