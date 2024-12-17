from typing import Dict, Optional, List
from ..base.base_fetcher import BaseFetcher

class BinanceFetcher:
    def __init__(self, spot_config: Dict, futures_config: Optional[Dict] = None):
        # Initialize spot API fetcher
        self.spot_fetcher = BaseFetcher(
            base_url=spot_config['base_url'],
            api_key=spot_config.get('api_key'),
            api_secret=spot_config.get('api_secret'),
            rate_limit=spot_config.get('rate_limit', 1200)
        )
        
        # Initialize futures API fetcher if configured
        self.futures_fetcher = None
        if futures_config:
            self.futures_fetcher = BaseFetcher(
                base_url=futures_config['base_url'],
                api_key=spot_config.get('api_key'),  # Use same keys as spot
                api_secret=spot_config.get('api_secret'),
                rate_limit=futures_config.get('rate_limit', 1200)
            )
        
    def _get_fetcher(self, market_type: str) -> BaseFetcher:
        """Get appropriate fetcher based on market type"""
        if market_type == 'futures':
            if not self.futures_fetcher:
                raise ValueError("Futures market not configured")
            return self.futures_fetcher
        return self.spot_fetcher
            
    def fetch_market_data(self, symbol: str, market_type: str = 'spot') -> Optional[Dict]:
        """Fetch comprehensive market data including price, volume, etc.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            market_type: 'spot' or 'futures'
            
        Returns:
            Dict containing market data or None on error
        """
        try:
            fetcher = self._get_fetcher(market_type)
            
            # Get 24hr ticker data
            endpoint = '/api/v3/ticker/24hr' if market_type == 'spot' else '/fapi/v1/ticker/24hr'
            ticker_data = fetcher.fetch_data(
                endpoint=endpoint,
                params={'symbol': symbol}
            )
            
            # For futures, get additional data
            if market_type == 'futures' and ticker_data:
                # Get funding rate
                funding_data = fetcher.fetch_data(
                    endpoint='/fapi/v1/fundingRate',
                    params={'symbol': symbol}
                )
                
                # Get open interest
                oi_data = fetcher.fetch_data(
                    endpoint='/fapi/v1/openInterest',
                    params={'symbol': symbol}
                )
                
                # Combine the data
                if funding_data and oi_data:
                    ticker_data['fundingRate'] = funding_data[0]['fundingRate']
                    ticker_data['openInterest'] = float(oi_data['openInterest'])
                    
            return ticker_data
            
        except Exception as e:
            self._get_fetcher(market_type).logger.error(
                f"Error fetching market data for {symbol}: {str(e)}"
            )
            return None
            
    def fetch_orderbook(self, symbol: str, limit: int = 100, 
                       market_type: str = 'spot') -> Optional[Dict]:
        """Fetch orderbook data
        
        Args:
            symbol: Trading pair symbol
            limit: Number of price levels to fetch
            market_type: 'spot' or 'futures'
            
        Returns:
            Dict containing orderbook data or None on error
        """
        try:
            fetcher = self._get_fetcher(market_type)
            endpoint = '/api/v3/depth' if market_type == 'spot' else '/fapi/v1/depth'
            
            data = fetcher.fetch_data(
                endpoint=endpoint,
                params={
                    'symbol': symbol,
                    'limit': limit
                }
            )
            return data
        except Exception as e:
            self._get_fetcher(market_type).logger.error(
                f"Error fetching orderbook for {symbol}: {str(e)}"
            )
            return None
            
    def fetch_recent_trades(self, symbol: str, limit: int = 100, 
                          market_type: str = 'spot') -> Optional[List[Dict]]:
        """Fetch recent trades
        
        Args:
            symbol: Trading pair symbol
            limit: Number of trades to fetch
            market_type: 'spot' or 'futures'
            
        Returns:
            List of trade dictionaries or None on error
        """
        try:
            fetcher = self._get_fetcher(market_type)
            endpoint = '/api/v3/trades' if market_type == 'spot' else '/fapi/v1/trades'
            
            data = fetcher.fetch_data(
                endpoint=endpoint,
                params={
                    'symbol': symbol,
                    'limit': limit
                }
            )
            return data
        except Exception as e:
            self._get_fetcher(market_type).logger.error(
                f"Error fetching trades for {symbol}: {str(e)}"
            )
            return None
    
    def fetch_liquidations(self, symbol: str, limit: int = 100) -> Optional[List[Dict]]:
        """Fetch recent liquidations (futures only)
        
        Args:
            symbol: Trading pair symbol
            limit: Number of liquidation events to fetch
            
        Returns:
            List of liquidation dictionaries or None on error
        """
        try:
            if not self.futures_fetcher:
                raise ValueError("Futures market not configured")
                
            data = self.futures_fetcher.fetch_data(
                endpoint='/fapi/v1/allForceOrders',
                params={
                    'symbol': symbol,
                    'limit': limit
                }
            )
            return data
        except Exception as e:
            if self.futures_fetcher:
                self.futures_fetcher.logger.error(
                    f"Error fetching liquidations for {symbol}: {str(e)}"
                )
            return None
    
    def fetch_funding_rate_history(self, symbol: str, 
                                 limit: int = 100) -> Optional[List[Dict]]:
        """Fetch funding rate history (futures only)
        
        Args:
            symbol: Trading pair symbol
            limit: Number of funding rate records to fetch
            
        Returns:
            List of funding rate dictionaries or None on error
        """
        try:
            if not self.futures_fetcher:
                raise ValueError("Futures market not configured")
                
            data = self.futures_fetcher.fetch_data(
                endpoint='/fapi/v1/fundingRate',
                params={
                    'symbol': symbol,
                    'limit': limit
                }
            )
            return data
        except Exception as e:
            if self.futures_fetcher:
                self.futures_fetcher.logger.error(
                    f"Error fetching funding rate history for {symbol}: {str(e)}"
                )
            return None
    
    def fetch_market_info(self, market_type: str = 'spot') -> Optional[Dict]:
        """Fetch exchange information including trading rules
        
        Args:
            market_type: 'spot' or 'futures'
            
        Returns:
            Dict containing exchange information or None on error
        """
        try:
            fetcher = self._get_fetcher(market_type)
            endpoint = '/api/v3/exchangeInfo' if market_type == 'spot' else '/fapi/v1/exchangeInfo'
            data = fetcher.fetch_data(endpoint=endpoint)
            return data
        except Exception as e:
            self._get_fetcher(market_type).logger.error(
                f"Error fetching {market_type} market info: {str(e)}"
            )
            return None