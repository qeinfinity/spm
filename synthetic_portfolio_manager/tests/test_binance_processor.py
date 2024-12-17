import pytest
from scripts.binance.processor import BinanceProcessor
from datetime import datetime

@pytest.fixture
def processor():
    return BinanceProcessor()

def test_process_spot_market_data(processor):
    raw_data = {
        "symbol": "BTCUSDT",
        "lastPrice": "50000.00",
        "price": "50000.00",
        "volume": "1000.00",
        "priceChange": "500.00",
        "highPrice": "51000.00",
        "lowPrice": "49000.00",
        "count": "50000",
        "closeTime": 1645084800000
    }
    
    processed = processor.process_market_data(raw_data, "BTCUSDT", "spot")
    
    assert processed["symbol"] == "BTCUSDT"
    assert processed["exchange"] == "binance"
    assert processed["type"] == "spot"
    assert processed["price"] == 50000.00
    assert processed["volume24h"] == 1000.00
    assert processed["priceChange24h"] == 500.00
    assert processed["price24hHigh"] == 51000.00
    assert processed["price24hLow"] == 49000.00
    assert processed["tradeCount24h"] == 50000
    assert processed["timestamp"] == 1645084800000
    assert "openInterest" not in processed
    assert "fundingRate" not in processed

def test_process_futures_market_data(processor):
    raw_data = {
        "symbol": "BTCUSDT",
        "lastPrice": "50000.00",
        "volume": "1000.00",
        "priceChange": "500.00",
        "highPrice": "51000.00",
        "lowPrice": "49000.00",
        "count": "50000",
        "closeTime": 1645084800000,
        "openInterest": "5000.00",
        "fundingRate": "0.0001"
    }
    
    processed = processor.process_market_data(raw_data, "BTCUSDT", "futures")
    
    assert processed["type"] == "futures"
    assert processed["openInterest"] == 5000.00
    assert processed["fundingRate"] == 0.0001

def test_process_orderbook_data(processor):
    raw_data = {
        "lastUpdateId": 1027024,
        "bids": [
            ["50000.00", "1.000"],
            ["49999.00", "1.500"]
        ],
        "asks": [
            ["50001.00", "0.500"],
            ["50002.00", "2.000"]
        ],
        "time": 1645084800000
    }
    
    processed = processor.process_orderbook_data(raw_data, "BTCUSDT", "spot")
    
    assert processed["symbol"] == "BTCUSDT"
    assert processed["type"] == "spot"
    assert len(processed["bids"]) == 2
    assert len(processed["asks"]) == 2
    assert processed["bids"][0][0] == 50000.00  # Price
    assert processed["bids"][0][1] == 1.000    # Quantity
    assert processed["lastUpdateId"] == 1027024
    assert processed["timestamp"] == 1645084800000

def test_process_trade_data(processor):
    raw_data = {
        "id": 28457,
        "price": "50000.00",
        "qty": "0.100",
        "time": 1645084800000,
        "isBuyerMaker": False
    }
    
    processed = processor.process_trade_data(raw_data, "BTCUSDT", "spot")
    
    assert processed["symbol"] == "BTCUSDT"
    assert processed["type"] == "spot"
    assert processed["price"] == 50000.00
    assert processed["quantity"] == 0.100
    assert processed["timestamp"] == 1645084800000
    assert processed["isBuyerMaker"] == False
    assert processed["tradeId"] == 28457

def test_process_market_data_with_missing_fields(processor):
    raw_data = {
        "symbol": "BTCUSDT",
        "lastPrice": "50000.00"
        # Missing most fields
    }
    
    processed = processor.process_market_data(raw_data, "BTCUSDT", "spot")
    
    assert processed["price"] == 50000.00
    assert processed["volume24h"] == 0.0  # Default value
    assert processed["priceChange24h"] == 0.0  # Default value

def test_process_orderbook_empty_data(processor):
    raw_data = {
        "lastUpdateId": 1027024,
        "bids": [],
        "asks": [],
        "time": 1645084800000
    }
    
    processed = processor.process_orderbook_data(raw_data, "BTCUSDT", "spot")
    
    assert len(processed["bids"]) == 0
    assert len(processed["asks"]) == 0

def test_invalid_market_type_processing(processor):
    raw_data = {"price": "50000.00"}
    
    with pytest.raises(ValueError, match="Invalid market type"):
        processor.process_market_data(raw_data, "BTCUSDT", "invalid")

def test_timestamp_conversion(processor):
    # Test ISO format timestamp
    iso_data = {"time": "2024-01-01T00:00:00Z"}
    processed = processor.process_market_data(iso_data, "BTCUSDT")
    assert isinstance(processed["timestamp"], int)
    
    # Test millisecond timestamp
    ms_data = {"time": 1645084800000}
    processed = processor.process_market_data(ms_data, "BTCUSDT")
    assert isinstance(processed["timestamp"], int)

def test_numeric_parsing(processor):
    # Test various numeric formats
    raw_data = {
        "symbol": "BTCUSDT",
        "lastPrice": "50000.00",  # String decimal
        "volume": 1000,           # Integer
        "priceChange": 500.50,    # Float
        "count": None,            # None value
        "closeTime": 1645084800000
    }
    
    processed = processor.process_market_data(raw_data, "BTCUSDT")
    
    assert isinstance(processed["price"], float)
    assert isinstance(processed["volume24h"], float)
    assert isinstance(processed["priceChange24h"], float)
    assert isinstance(processed["tradeCount24h"], int)

def test_process_trade_data_array(processor):
    raw_trades = [
        {
            "id": 28457,
            "price": "50000.00",
            "qty": "0.100",
            "time": 1645084800000,
            "isBuyerMaker": False
        },
        {
            "id": 28458,
            "price": "50001.00",
            "qty": "0.200",
            "time": 1645084801000,
            "isBuyerMaker": True
        }
    ]
    
    processed_trades = [
        processor.process_trade_data(trade, "BTCUSDT", "spot")
        for trade in raw_trades
    ]
    
    assert len(processed_trades) == 2
    assert processed_trades[0]["tradeId"] == 28457
    assert processed_trades[1]["tradeId"] == 28458
    assert processed_trades[0]["quantity"] == 0.100
    assert processed_trades[1]["quantity"] == 0.200