from scripts.binance.fetcher import BinanceFetcher
from scripts.binance.cache import BinanceCache

def main():
    fetcher = BinanceFetcher()
    cache = BinanceCache()

    symbol = "BTCUSDT"
    data = fetcher.fetch_symbol(symbol)
    if data:
        cache.save_to_cache(data, f"{symbol.lower()}_latest")
        print(f"Fetched and cached data: {data}")
    else:
        print("Failed to fetch Binance data.")

if __name__ == "__main__":
    main()