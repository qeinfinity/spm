#!/bin/bash

# Create main project directory
mkdir -p synthetic_portfolio_manager
cd synthetic_portfolio_manager

# Create main directories
mkdir -p data/{processed,raw,cache/{binance,coinmarketcap,fred}}
mkdir -p logs
mkdir -p models
mkdir -p scripts/{base,binance,coinmarketcap,fred}
mkdir -p utilities
mkdir -p tests

# Create main.py
cat > main.py << 'EOF'
def main():
    """Main entry point to coordinate pipeline execution."""
    pass

if __name__ == "__main__":
    main()
EOF

# Create base classes
mkdir -p scripts/base
cat > scripts/base/base_fetcher.py << 'EOF'
from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    """Abstract base class for all fetchers."""
    
    @abstractmethod
    def fetch(self):
        """Fetch data from the API."""
        pass
EOF

cat > scripts/base/base_scraper.py << 'EOF'
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    @abstractmethod
    def scrape(self):
        """Scrape and normalize data."""
        pass
EOF

cat > scripts/base/base_cache.py << 'EOF'
from abc import ABC, abstractmethod

class BaseCache(ABC):
    """Abstract base class for caching mechanisms."""
    
    @abstractmethod
    def get(self, key):
        """Retrieve item from cache."""
        pass
    
    @abstractmethod
    def set(self, key, value):
        """Store item in cache."""
        pass
EOF

# Create __init__.py for scripts package
touch scripts/__init__.py

# Function to create service-specific files
create_service_files() {
    local service=$1
    
    cat > scripts/${service}/fetcher.py << EOF
from scripts.base.base_fetcher import BaseFetcher

class ${service^}Fetcher(BaseFetcher):
    def fetch(self):
        """Fetch data from ${service^} API."""
        pass
EOF

    cat > scripts/${service}/scraper.py << EOF
from scripts.base.base_scraper import BaseScraper

class ${service^}Scraper(BaseScraper):
    def scrape(self):
        """Scrape and normalize ${service^} data."""
        pass
EOF

    cat > scripts/${service}/cache.py << EOF
from scripts.base.base_cache import BaseCache

class ${service^}Cache(BaseCache):
    def get(self, key):
        """Retrieve ${service^} data from cache."""
        pass
        
    def set(self, key, value):
        """Store ${service^} data in cache."""
        pass
EOF
}

# Create service-specific files
for service in binance coinmarketcap fred; do
    create_service_files $service
done

# Create utility files
cat > utilities/config.py << 'EOF'
"""Centralized configuration for API keys, endpoints, and paths."""

class Config:
    # API Keys
    BINANCE_API_KEY = "your_binance_api_key"
    COINMARKETCAP_API_KEY = "your_coinmarketcap_api_key"
    FRED_API_KEY = "your_fred_api_key"
    
    # API Endpoints
    BINANCE_ENDPOINT = "https://api.binance.com"
    COINMARKETCAP_ENDPOINT = "https://pro-api.coinmarketcap.com"
    FRED_ENDPOINT = "https://api.stlouisfed.org"
    
    # Paths
    DATA_DIR = "data"
    CACHE_DIR = "data/cache"
    LOGS_DIR = "logs"
EOF

cat > utilities/logger.py << 'EOF'
"""Custom logger for all modules."""

import logging
import os
from datetime import datetime

def setup_logger(name, log_file):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    return logger
EOF

cat > utilities/scheduler.py << 'EOF'
"""Scheduler for periodic API fetches."""

from apscheduler.schedulers.background import BackgroundScheduler

class DataFetchScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def schedule_fetch(self, fetcher, interval_minutes):
        """Schedule periodic data fetches."""
        self.scheduler.add_job(
            fetcher.fetch,
            'interval',
            minutes=interval_minutes
        )
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
EOF

# Create requirements.txt
cat > utilities/requirements.txt << 'EOF'
requests>=2.25.1
pandas>=1.2.4
numpy>=1.20.2
apscheduler>=3.8.1
python-binance>=1.0.15
coinmarketcap>=5.0.3
fredapi>=0.5.0
pytest>=6.2.5
EOF

# Create test files
cat > tests/test_base.py << 'EOF'
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
EOF

# Function to create service-specific test files
create_test_file() {
    local service=$1
    
    cat > tests/test_${service}.py << EOF
"""Tests for ${service^} components."""

import pytest
from scripts.${service}.fetcher import ${service^}Fetcher
from scripts.${service}.scraper import ${service^}Scraper
from scripts.${service}.cache import ${service^}Cache

def test_${service}_fetcher():
    """Test ${service^}Fetcher implementation."""
    fetcher = ${service^}Fetcher()
    assert fetcher.fetch() is None

def test_${service}_scraper():
    """Test ${service^}Scraper implementation."""
    scraper = ${service^}Scraper()
    assert scraper.scrape() is None

def test_${service}_cache():
    """Test ${service^}Cache implementation."""
    cache = ${service^}Cache()
    assert cache.get("test_key") is None
    assert cache.set("test_key", "test_value") is None
EOF
}

# Create service-specific test files
for service in binance coinmarketcap fred; do
    create_test_file $service
done

# Create log files
touch logs/api_calls.log
touch logs/errors.log
touch logs/pipeline.log

# Make the script executable
chmod +x init_project_structure.sh

echo "Project structure created successfully!"