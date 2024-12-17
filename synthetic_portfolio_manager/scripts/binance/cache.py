from scripts.base.base_cache import BaseCache

class BinanceCache(BaseCache):
    def __init__(self, directory: str = 'data/cache/binance', max_age_hours: int = 24, compress: bool = False):
        """Initialize Binance cache
        
        Args:
            directory: Base directory for cache
            max_age_hours: Maximum age of cache files in hours
            compress: Whether to compress cached files
        """
        super().__init__(directory)
        self.max_age_hours = max_age_hours
        self.compress = compress