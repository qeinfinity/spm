from typing import Dict, Optional
from dataclasses import dataclass
import os
import yaml

@dataclass
class APIConfig:
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: str = ''
    rate_limit: int = 1200

@dataclass
class Config:
    binance: APIConfig
    coinglass: APIConfig
    
    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(
            binance=APIConfig(**data.get('binance', {})),
            coinglass=APIConfig(**data.get('coinglass', {}))
        )

    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        return cls(
            binance=APIConfig(
                api_key=os.getenv('BINANCE_API_KEY'),
                api_secret=os.getenv('BINANCE_API_SECRET'),
                base_url='https://api.binance.com',
                rate_limit=int(os.getenv('BINANCE_RATE_LIMIT', '1200'))
            ),
            coinglass=APIConfig(
                api_key=os.getenv('COINGLASS_API_KEY'),
                base_url='https://open-api.coinglass.com',
                rate_limit=int(os.getenv('COINGLASS_RATE_LIMIT', '100'))
            )
        )