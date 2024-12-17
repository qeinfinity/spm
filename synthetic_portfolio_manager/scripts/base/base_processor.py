from typing import Dict, List, Union, Optional, Tuple
from datetime import datetime

class BaseProcessor:
    def process_market_data(self, raw_data: Dict, symbol: str, market_type: str = 'spot') -> Dict:
        """Process raw market data into standardized format
        
        Returns:
        {
            symbol: str
            exchange: str
            type: 'spot' | 'futures'
            price: float
            timestamp: int  # milliseconds since epoch
            volume24h: float
            volumeDelta24h: Optional[float]
            priceChange24h: float
            priceChange1h: Optional[float]
            price24hHigh: float
            price24hLow: float
            tradeCount24h: int
            bidAskSpread: Optional[float]
            openInterest: Optional[float]
            fundingRate: Optional[float]
            liquidations24h: Optional[float]
        }
        """
        raise NotImplementedError
    
    def process_orderbook_data(self, raw_data: Dict, symbol: str, market_type: str = 'spot') -> Dict:
        """Process raw orderbook data into standardized format
        
        Returns:
        {
            symbol: str
            type: 'spot' | 'futures'
            bids: List[Tuple[float, float]]  # price, quantity pairs
            asks: List[Tuple[float, float]]  # price, quantity pairs
            timestamp: int  # milliseconds since epoch
            lastUpdateId: int
        }
        """
        raise NotImplementedError
    
    def process_trade_data(self, raw_data: Dict, symbol: str, market_type: str = 'spot') -> Dict:
        """Process raw trade data into standardized format
        
        Returns:
        {
            symbol: str
            type: 'spot' | 'futures'
            price: float
            quantity: float
            timestamp: int  # milliseconds since epoch
            isBuyerMaker: bool
            tradeId: int
        }
        """
        raise NotImplementedError
    
    def _convert_timestamp(self, ts: Union[int, str]) -> int:
        """Convert various timestamp formats to milliseconds since epoch"""
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        return int(ts)  # Assume milliseconds if already numeric
    
    def _parse_numeric(self, value: Union[str, float, int], default: float = 0.0) -> float:
        """Safely parse numeric values"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def _validate_market_type(self, market_type: str) -> str:
        """Validate and normalize market type"""
        if market_type.lower() not in ['spot', 'futures']:
            raise ValueError(f"Invalid market type: {market_type}. Must be 'spot' or 'futures'")
        return market_type.lower()