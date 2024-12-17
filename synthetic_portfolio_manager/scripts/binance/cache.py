from scripts.base.base_cache import BaseCache

class BinanceCache(BaseCache):
    def __init__(self):
        super().__init__("data/cache/binance")

# Example usage
if __name__ == "__main__":
    cache = BinanceCache()
    cache.save_to_cache({"price": "19800"}, "btc_price")
    print(cache.load_from_cache("btc_price"))