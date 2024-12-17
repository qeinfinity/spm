import argparse
import logging
import time
from pathlib import Path
from config.settings import Config, MarketType, DataType
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
        '--symbol',
        type=str,
        help='Trading symbol to fetch data for (overrides config)'
    )
    parser.add_argument(
        '--market-type',
        type=str,
        choices=['spot', 'futures'],
        help='Market type to fetch data from (overrides config)'
    )
    return parser.parse_args()

def fetch_and_process_data(fetcher: BinanceFetcher, processor: BinanceProcessor, 
                          cache: BinanceCache, symbol: str, 
                          market_type: MarketType, data_types: list[DataType]) -> None:
    """Fetch, process, and cache market data
    
    Args:
        fetcher: Initialized BinanceFetcher instance
        processor: Initialized BinanceProcessor instance
        cache: Initialized BinanceCache instance
        symbol: Trading symbol (e.g., 'BTCUSDT')
        market_type: Market type (spot or futures)
        data_types: List of data types to collect
    """
    logger = get_logger('data_pipeline')
    
    try:
        # Fetch market data if requested
        if DataType.MARKET in data_types:
            logger.info(f"Fetching {market_type.value} market data for {symbol}")
            market_data = fetcher.fetch_market_data(symbol, market_type.value)
            if market_data:
                # Cache raw data
                cache.save_to_cache(
                    market_data,
                    f"{symbol.lower()}_market",
                    DataType.MARKET.value,
                    is_processed=False
                )
                logger.debug(f"Cached raw market data for {symbol}")
                
                # Process and cache processed data
                processed_data = processor.process_market_data(
                    market_data, symbol, market_type.value
                )
                cache.save_to_cache(
                    processed_data,
                    f"{symbol.lower()}_market",
                    DataType.MARKET.value,
                    is_processed=True
                )
                logger.debug(f"Cached processed market data for {symbol}")
            
        # Fetch and process orderbook if requested
        if DataType.ORDERBOOK in data_types:
            logger.info(f"Fetching {market_type.value} orderbook for {symbol}")
            orderbook_data = fetcher.fetch_orderbook(symbol, market_type=market_type.value)
            if orderbook_data:
                cache.save_to_cache(
                    orderbook_data,
                    f"{symbol.lower()}_orderbook",
                    DataType.ORDERBOOK.value,
                    is_processed=False
                )
                
                processed_orderbook = processor.process_orderbook_data(
                    orderbook_data, symbol, market_type.value
                )
                cache.save_to_cache(
                    processed_orderbook,
                    f"{symbol.lower()}_orderbook",
                    DataType.ORDERBOOK.value,
                    is_processed=True
                )
                logger.debug(f"Cached orderbook data for {symbol}")
            
        # Fetch and process trades if requested
        if DataType.TRADE in data_types:
            logger.info(f"Fetching {market_type.value} recent trades for {symbol}")
            trades_data = fetcher.fetch_recent_trades(symbol, market_type=market_type.value)
            if trades_data:
                cache.save_to_cache(
                    trades_data,
                    f"{symbol.lower()}_trades",
                    DataType.TRADE.value,
                    is_processed=False
                )
                
                processed_trades = [
                    processor.process_trade_data(trade, symbol, market_type.value)
                    for trade in trades_data
                ]
                cache.save_to_cache(
                    processed_trades,
                    f"{symbol.lower()}_trades",
                    DataType.TRADE.value,
                    is_processed=True
                )
                logger.debug(f"Cached recent trades for {symbol}")
            
        # If futures market, fetch additional data
        if market_type == MarketType.FUTURES:
            logger.info(f"Fetching futures-specific data for {symbol}")
            liquidations = fetcher.fetch_liquidations(symbol)
            if liquidations:
                cache.save_to_cache(
                    liquidations,
                    f"{symbol.lower()}_liquidations",
                    DataType.MARKET.value,
                    is_processed=False
                )
                logger.debug(f"Cached liquidations data for {symbol}")
                
        logger.info(f"Completed data pipeline for {symbol} {market_type.value}")
        
    except Exception as e:
        logger.error(f"Error in data pipeline for {symbol}: {str(e)}")
        raise

def setup_components(config: Config):
    """Initialize system components based on configuration
    
    Args:
        config: Application configuration
        
    Returns:
        tuple: (BinanceFetcher, BinanceProcessor, BinanceCache)
    """
    # Set up fetcher with appropriate URLs based on market type
    spot_config = {
        'api_key': config.binance.api_key,
        'api_secret': config.binance.api_secret,
        'base_url': config.binance.base_url,
        'rate_limit': config.binance.rate_limit
    }
    
    # Add futures config if available
    futures_config = None
    if config.binance.futures:
        futures_config = {
            'base_url': config.binance.futures.base_url,
            'rate_limit': config.binance.futures.rate_limit
        }
    
    fetcher = BinanceFetcher(
        spot_config=spot_config,
        futures_config=futures_config
    )
    
    processor = BinanceProcessor()
    
    cache = BinanceCache(
        directory=config.cache.directory,
        max_age_hours=config.cache.max_age_hours,
        compress=config.cache.compress
    )
    
    return fetcher, processor, cache

def main():
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        config = Config.from_yaml(str(config_path))
        
        # Setup logging based on config
        setup_logging(
            level=config.logging.level.value,
            log_dir=config.logging.directory,
            max_bytes=config.logging.max_file_size * 1024 * 1024,  # Convert MB to bytes
            backup_count=config.logging.backup_count
        )
        logger = get_logger('main')
        logger.info(f"Loaded configuration from {config_path}")
        
        # Initialize components
        fetcher, processor, cache = setup_components(config)
        logger.info("Initialized all components successfully")
        
        # Determine market type (command line overrides config)
        market_type = MarketType[args.market_type.upper()] if args.market_type else config.data.default_market
        
        # Process each configured symbol
        symbols = [args.symbol] if args.symbol else config.data.symbols
        for symbol in symbols:
            try:
                fetch_and_process_data(
                    fetcher=fetcher,
                    processor=processor,
                    cache=cache,
                    symbol=symbol,
                    market_type=market_type,
                    data_types=config.data.types
                )
                
                # Sleep between symbols to respect rate limits
                if symbol != symbols[-1]:  # Don't sleep after last symbol
                    time.sleep(1)  # Basic rate limiting
                    
            except Exception as e:
                logger.error(f"Failed to process symbol {symbol}: {str(e)}")
                # Continue with next symbol on error
                continue
        
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()