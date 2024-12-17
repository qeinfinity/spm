from typing import Dict, Optional, List
from ..base.base_fetcher import BaseFetcher

class BinanceFetcher(BaseFetcher):
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 rate_limit: int = 1200):
        # Initialize spot API
        super().__init__(
            base_url='https://api.binance.com/api/v3',
            api_key=api_key,
            api_secret=api_secret,
            rate_limit=rate_limit
        )
        # Initialize futures API
        self.futures_url = 'https://fapi.binance.com/fapi/v1'
        
    def fetch_market_data(self, symbol: str, market_type: str = 'spot') -> Optional[Dict]:
        """Fetch comprehensive market data including price, volume, etc."""
        try:
            # Get 24hr ticker data
            base_url = self.futures_url if market_type == 'futures' else self.base_url
            ticker_endpoint = '/ticker/24hr'
            ticker_data = self.fetch_data(
                endpoint=ticker_endpoint,
                params={'symbol': symbol},
                base_url=base_url
            )
            
            # For futures, get additional data
            if market_type == 'futures':
                # Get funding rate
                funding_data = self.fetch_data(
                    endpoint='/fundingRate',
                    params={'symbol': symbol},
                    base_url=self.futures_url
                )
                
                # Get open interest
                oi_data = self.fetch_data(
                    endpoint='/openInterest',
                    params={'symbol': symbol},
                    base_url=self.futures_url
                )
                
                # Combine the data
                if ticker_data and funding_data and oi_data:
                    ticker_data['fundingRate'] = funding_data[0]['fundingRate']
                    ticker_data['openInterest'] = float(oi_data['openInterest'])
                    
            return ticker_data
            
        except Exception as e:
            self.logger.error(f"Error fetching market data for {symbol}: {str(e)}")
            return None
            
    def fetch_orderbook(self, symbol: str, limit: int = 100, 
                       market_type: str = 'spot') -> Optional[Dict]:
        """Fetch orderbook data"""
        try:
            base_url = self.futures_url if market_type == 'futures' else self.base_url
            data = self.fetch_data(
                endpoint='/depth',
                params={
                    'symbol': symbol,
                    'limit': limit
                },
                base_url=base_url
            )
            return data
        except Exception as e:
            self.logger.error(f"Error fetching orderbook for {symbol}: {str(e)}")
            return None
            
    def fetch_recent_trades(self, symbol: str, limit: int = 100, 
                          market_type: str = 'spot') -> Optional[List[Dict]]:
        """Fetch recent trades"""
        try:
            base_url = self.futures_url if market_type == 'futures' else self.base_url
            data = self.fetch_data(
                endpoint='/trades',
                params={
                    'symbol': symbol,
                    'limit': limit
                },
                base_url=base_url
            )
            return data
        except Exception as e:
            self.logger.error(f"Error fetching trades for {symbol}: {str(e)}")
            return None
    
    def fetch_liquidations(self, symbol: str) -> Optional[List[Dict]]:
        """Fetch recent liquidations (futures only)"""
        try:
            data = self.fetch_data(
                endpoint='/allForceOrders',
                params={'symbol': symbol},
                base_url=self.futures_url
            )
            return data
        except Exception as e:
            self.logger.error(f"Error fetching liquidations for {symbol}: {str(e)}")
            return None
            
    def fetch_data(self, endpoint: str, params: Optional[Dict] = None, 
                  base_url: Optional[str] = None, **kwargs) -> Optional[Dict]:
        """Override fetch_data to handle different base URLs"""
        original_base_url = self.base_url
        if base_url:
            self.base_url = base_url
        try:
            return super().fetch_data(endpoint, params, **kwargs)
        finally:
            self.base_url = original_base_url  # Restore original base URL