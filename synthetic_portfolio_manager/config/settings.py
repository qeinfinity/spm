from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import os
import yaml

class MarketType(Enum):
    SPOT = 'spot'
    FUTURES = 'futures'

class DataType(Enum):
    MARKET = 'market'
    ORDERBOOK = 'orderbook'
    TRADE = 'trade'

class LogLevel(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'

@dataclass
class MarketConfig:
    base_url: str
    rate_limit: int

@dataclass
class APIConfig:
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: str = ''
    rate_limit: int = 1200
    futures: Optional[MarketConfig] = None

@dataclass
class LoggingConfig:
    level: LogLevel = LogLevel.INFO
    directory: str = 'logs'
    max_file_size: int = 10  # MB
    backup_count: int = 5

@dataclass
class CacheConfig:
    directory: str = 'data/cache'
    max_age_hours: int = 24
    compress: bool = False

@dataclass
class DataCollectionIntervals:
    market: int = 60  # seconds
    orderbook: int = 30
    trade: int = 15

@dataclass
class DataConfig:
    default_market: MarketType = MarketType.SPOT
    default_symbol: str = 'BTCUSDT'
    symbols: List[str] = None
    types: List[DataType] = None
    intervals: DataCollectionIntervals = DataCollectionIntervals()
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        if self.types is None:
            self.types = [DataType.MARKET, DataType.ORDERBOOK, DataType.TRADE]

@dataclass
class Config:
    binance: APIConfig
    coinglass: APIConfig
    logging: LoggingConfig = LoggingConfig()
    cache: CacheConfig = CacheConfig()
    data: DataConfig = DataConfig()
    
    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            
        # Process API configurations
        binance_data = data.get('binance', {})
        futures_data = binance_data.pop('futures', None)
        binance_config = APIConfig(**binance_data)
        if futures_data:
            binance_config.futures = MarketConfig(**futures_data)
            
        coinglass_data = data.get('coinglass', {})
        coinglass_config = APIConfig(**coinglass_data)
        
        # Process logging configuration
        logging_data = data.get('logging', {})
        if 'level' in logging_data:
            logging_data['level'] = LogLevel[logging_data['level']]
        logging_config = LoggingConfig(**logging_data)
        
        # Process cache configuration
        cache_config = CacheConfig(**data.get('cache', {}))
        
        # Process data collection configuration
        data_config = data.get('data', {})
        if 'default_market' in data_config:
            data_config['default_market'] = MarketType[data_config['default_market'].upper()]
        if 'types' in data_config:
            data_config['types'] = [DataType[t.upper()] for t in data_config['types']]
        if 'intervals' in data_config:
            data_config['intervals'] = DataCollectionIntervals(**data_config['intervals'])
            
        return cls(
            binance=binance_config,
            coinglass=coinglass_config,
            logging=logging_config,
            cache=cache_config,
            data=DataConfig(**data_config)
        )

    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        return cls(
            binance=APIConfig(
                api_key=os.getenv('BINANCE_API_KEY'),
                api_secret=os.getenv('BINANCE_API_SECRET'),
                base_url=os.getenv('BINANCE_BASE_URL', 'https://api.binance.com'),
                rate_limit=int(os.getenv('BINANCE_RATE_LIMIT', '1200')),
                futures=MarketConfig(
                    base_url=os.getenv('BINANCE_FUTURES_URL', 'https://fapi.binance.com'),
                    rate_limit=int(os.getenv('BINANCE_FUTURES_RATE_LIMIT', '1200'))
                ) if os.getenv('BINANCE_FUTURES_URL') else None
            ),
            coinglass=APIConfig(
                api_key=os.getenv('COINGLASS_API_KEY'),
                base_url=os.getenv('COINGLASS_BASE_URL', 'https://open-api.coinglass.com'),
                rate_limit=int(os.getenv('COINGLASS_RATE_LIMIT', '100'))
            )
        )