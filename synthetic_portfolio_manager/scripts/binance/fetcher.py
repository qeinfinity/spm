from scripts.base.base_fetcher import BaseFetcher

class BinanceFetcher(BaseFetcher):
    def __init__(self):
        super().__init__("https://api.binance.com/api/v3/ticker/price")

    def fetch_symbol(self, symbol):
        return self.fetch_data(params={"symbol": symbol})

# Example usage
if __name__ == "__main__":
    fetcher = BinanceFetcher()
    data = fetcher.fetch_symbol("BTCUSDT")
    print(data)
