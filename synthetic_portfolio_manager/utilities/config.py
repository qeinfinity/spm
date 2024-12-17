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
