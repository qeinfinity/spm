from typing import Dict, List, Union, Optional, Tuple
from ..base.base_processor import BaseProcessor

class BinanceProcessor(BaseProcessor):
    def __init__(self, exchange_name: str = 'binance'):
        self.exchange_name = exchange_name
    
    def process_market_data(self, raw_data: Dict, symbol: str, market_type: str = 'spot') -> Dict:
        """Process Binance market data into standardized format"""
        market_type = self._validate_market_type(market_type)
        
        result = {
            'symbol': symbol,
            'exchange': self.exchange_name,
            'type': market_type,
            'price': self._parse_numeric(raw_data.get('lastPrice') or raw_data.get('price')),
            'timestamp': self._convert_timestamp(raw_data.get('closeTime') or raw_data.get('time')),
            'volume24h': self._parse_numeric(raw_data.get('volume')),
            'priceChange24h': self._parse_numeric(raw_data.get('priceChange')),
            'price24hHigh': self._parse_numeric(raw_data.get('highPrice')),
            'price24hLow': self._parse_numeric(raw_data.get('lowPrice')),
            'tradeCount24h': int(float(raw_data.get('count', 0))),
            'volumeDelta24h': None,  # Calculate if needed
            'priceChange1h': None,  # Not directly available
        }
        
        # Add futures-specific fields if available
        if market_type == 'futures':
            result.update({
                'openInterest': self._parse_numeric(raw_data.get('openInterest')),
                'fundingRate': self._parse_numeric(raw_data.get('fundingRate')),
                'liquidations24h': self._parse_numeric(raw_data.get('totalLiquidations'))
            })
        
        return result
    
    def process_orderbook_data(self, raw_data: Dict, symbol: str, market_type: str = 'spot') -> Dict:
        """Process Binance orderbook data into standardized format"""
        market_type = self._validate_market_type(market_type)
        
        # Convert price and quantity strings to floats
        bids = [[float(price), float(qty)] for price, qty in raw_data.get('bids', [])]
        asks = [[float(price), float(qty)] for price, qty in raw_data.get('asks', [])]
        
        return {
            'symbol': symbol,
            'type': market_type,
            'bids': bids,
            'asks': asks,
            'timestamp': self._convert_timestamp(raw_data.get('time', raw_data.get('E', 0))),
            'lastUpdateId': int(raw_data.get('lastUpdateId', 0))
        }
    
    def process_trade_data(self, raw_data: Dict, symbol: str, market_type: str = 'spot') -> Dict:
        """Process Binance trade data into standardized format"""
        market_type = self._validate_market_type(market_type)
        
        return {
            'symbol': symbol,
            'type': market_type,
            'price': self._parse_numeric(raw_data['price']),
            'quantity': self._parse_numeric(raw_data.get('qty') or raw_data.get('quantity')),
            'timestamp': self._convert_timestamp(raw_data.get('time', 0)),
            'isBuyerMaker': bool(raw_data.get('isBuyerMaker')),
            'tradeId': int(raw_data.get('id', 0))
        }
    
    def process_liquidation_data(self, raw_data: List[Dict], timeframe_ms: int = 86400000) -> float:
        """Process liquidation data to get total liquidations in specified timeframe
        
        Args:
            raw_data: List of liquidation events
            timeframe_ms: Timeframe in milliseconds (default: 24h)
        
        Returns:
            Total liquidation volume in specified timeframe
        """
        current_time = int(time.time() * 1000)
        cutoff_time = current_time - timeframe_ms
        
        total_liquidations = sum(
            self._parse_numeric(event.get('quantity', 0)) * self._parse_numeric(event.get('price', 0))
            for event in raw_data
            if self._convert_timestamp(event.get('time', 0)) >= cutoff_time
        )
        
        return total_liquidations