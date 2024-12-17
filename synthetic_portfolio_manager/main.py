import argparse
import logging
from pathlib import Path
from config.settings import Config
from utilities.logging_config import setup_logging, get_logger
from scripts.binance.fetcher import BinanceFetcher
from scripts.binance.processor import BinanceProcessor
from scripts.binance.cache import BinanceCache

def parse_args():
    parser = argparse.ArgumentParser(description='Synthetic Portfolio Manager')
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    parser.add_argument(
        '--symbol',
        type=str,
        default='BTCUSDT',
        help='Trading symbol to fetch data for'
    )
    parser.add_argument(
        '--market-type',
        type=str,
        default='spot',
        choices=['spot', 'futures'],
        help='Market type to fetch data from'
    )
    return parser.parse_args()

def fetch_and_process_data(fetcher: BinanceFetcher, processor: BinanceProcessor, 
                         cache: BinanceCache, symbol: str, market_type: str) -> None:
    """Fetch, process, and cache market data
    
    Args:
        fetcher: Initialized BinanceFetcher instance
        processor: Initialized BinanceProcessor instance
        cache: Initialized BinanceCache instance
        symbol: Trading symbol (e.g., 'BTCUSDT')
        market_type: Market type ('spot' or 'futures')
    """
    logger = get_logger('data_pipeline')
    
    try:
        # Fetch market data
        logger.info(f"Fetching {market_type} market data for {symbol}")
        market_data = fetcher.fetch_market_data(symbol, market_type)
        if not market_data:
            raise ValueError(f"Failed to fetch market data for {symbol}")
            
        # Cache raw data
        cache.save_to_cache(
            market_data,
            f"{symbol.lower()}_market",
            "market",
            is_processed=False
        )
        logger.debug(f"Cached raw market data for {symbol}")
        
        # Process data
        processed_data = processor.process_market_data(market_data, symbol, market_type)
        
        # Cache processed data
        cache.save_to_cache(
            processed_data,
            f"{symbol.lower()}_market",
            "market",
            is_processed=True
        )
        logger.debug(f"Cached processed market data for {symbol}")
        
        # Fetch and process orderbook
        logger.info(f"Fetching {market_type} orderbook for {symbol}")
        orderbook_data = fetcher.fetch_orderbook(symbol, market_type=market_type)
        if orderbook_data:
            processed_orderbook = processor.process_orderbook_data(
                orderbook_data, symbol, market_type
            )
            cache.save_to_cache(
                processed_orderbook,
                f"{symbol.lower()}_orderbook",
                "orderbook",
                is_processed=True
            )
            logger.debug(f"Cached orderbook data for {symbol}")
            
        # Fetch and process recent trades
        logger.info(f"Fetching {market_type} recent trades for {symbol}")
        trades_data = fetcher.fetch_recent_trades(symbol, market_type=market_type)
        if trades_data:
            processed_trades = [
                processor.process_trade_data(trade, symbol, market_type)
                for trade in trades_data
            ]
            cache.save_to_cache(
                processed_trades,
                f"{symbol.lower()}_trades",
                "trade",
                is_processed=True
            )
            logger.debug(f"Cached recent trades for {symbol}")
            
        # If futures market, fetch additional data
        if market_type == 'futures':
            logger.info(f"Fetching futures-specific data for {symbol}")
            liquidations = fetcher.fetch_liquidations(symbol)
            if liquidations:
                cache.save_to_cache(
                    liquidations,
                    f"{symbol.lower()}_liquidations",
                    "market",
                    is_processed=False
                )
                logger.debug(f"Cached liquidations data for {symbol}")
                
        logger.info(f"Completed data pipeline for {symbol} {market_type}")
        
    except Exception as e:
        logger.error(f"Error in data pipeline for {symbol}: {str(e)}")
        raise

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Setup logging
    log_level = getattr(logging, args.log_level.upper())
    setup_logging(level=log_level)
    logger = get_logger('main')
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        config = Config.from_yaml(str(config_path))
        logger.info(f"Loaded configuration from {config_path}")
        
        # Initialize components
        fetcher = BinanceFetcher(
            api_key=config.binance.api_key,
            api_secret=config.binance.api_secret,
            rate_limit=config.binance.rate_limit
        )
        processor = BinanceProcessor()
        cache = BinanceCache()
        
        logger.info("Initialized all components successfully")
        
        # Fetch and process data
        fetch_and_process_data(
            fetcher=fetcher,
            processor=processor,
            cache=cache,
            symbol=args.symbol,
            market_type=args.market_type
        )
        
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()