import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from scripts.binance.fetcher import BinanceFetcher

@pytest.fixture
def mock_response():
    return Mock()

@pytest.fixture
def fetcher():
    return BinanceFetcher()

def test_fetch_market_data_spot(fetcher, mock_response):
    # Mock data
    mock_ticker_data = {
        "symbol": "BTCUSDT",
        "lastPrice": "50000.00",
        "volume": "1000.00",
        "priceChange": "500.00",
        "highPrice": "51000.00",
        "lowPrice": "49000.00",
        "count": "50000",
        "closeTime": 1645084800000
    }
    
    with patch('requests.Session.request') as mock_request:
        mock_response.json.return_value = mock_ticker_data
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        data = fetcher.fetch_market_data("BTCUSDT", "spot")
        
        assert data is not None
        assert data['lastPrice'] == "50000.00"
        assert data['volume'] == "1000.00"
        mock_request.assert_called_once()

def test_fetch_market_data_futures(fetcher, mock_response):
    # Mock data
    mock_ticker_data = {
        "symbol": "BTCUSDT",
        "lastPrice": "50000.00",
        "volume": "1000.00",
        "priceChange": "500.00",
        "highPrice": "51000.00",
        "lowPrice": "49000.00",
        "count": "50000",
        "closeTime": 1645084800000
    }
    
    mock_funding_data = [{
        "symbol": "BTCUSDT",
        "fundingRate": "0.0001",
        "fundingTime": 1645084800000
    }]
    
    mock_oi_data = {
        "symbol": "BTCUSDT",
        "openInterest": "1000.00",
        "time": 1645084800000
    }
    
    with patch('requests.Session.request') as mock_request:
        def side_effect(*args, **kwargs):
            url = kwargs.get('url', '')
            if 'ticker/24hr' in url:
                mock_response.json.return_value = mock_ticker_data
            elif 'fundingRate' in url:
                mock_response.json.return_value = mock_funding_data
            elif 'openInterest' in url:
                mock_response.json.return_value = mock_oi_data
            return mock_response
            
        mock_response.status_code = 200
        mock_request.side_effect = side_effect
        
        data = fetcher.fetch_market_data("BTCUSDT", "futures")
        
        assert data is not None
        assert 'fundingRate' in data
        assert 'openInterest' in data
        assert data['fundingRate'] == "0.0001"
        assert data['openInterest'] == 1000.0

def test_fetch_orderbook(fetcher, mock_response):
    mock_orderbook_data = {
        "lastUpdateId": 1027024,
        "bids": [
            ["50000.00", "1.000"],
            ["49999.00", "1.500"]
        ],
        "asks": [
            ["50001.00", "0.500"],
            ["50002.00", "2.000"]
        ]
    }
    
    with patch('requests.Session.request') as mock_request:
        mock_response.json.return_value = mock_orderbook_data
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        data = fetcher.fetch_orderbook("BTCUSDT")
        
        assert data is not None
        assert len(data['bids']) == 2
        assert len(data['asks']) == 2
        assert data['lastUpdateId'] == 1027024

def test_fetch_recent_trades(fetcher, mock_response):
    mock_trades_data = [
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
    
    with patch('requests.Session.request') as mock_request:
        mock_response.json.return_value = mock_trades_data
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        data = fetcher.fetch_recent_trades("BTCUSDT")
        
        assert data is not None
        assert len(data) == 2
        assert data[0]['id'] == 28457
        assert data[0]['price'] == "50000.00"

def test_rate_limiting(fetcher):
    # Test rate limiting by making multiple rapid requests
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"price": "50000.00"}
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        start_time = datetime.now()
        
        # Make multiple requests that should trigger rate limiting
        for _ in range(5):
            fetcher.fetch_market_data("BTCUSDT")
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Verify that rate limiting added some delay
        assert duration > 0.1  # Arbitrary small delay to verify rate limiting

def test_error_handling(fetcher, mock_response):
    with patch('requests.Session.request') as mock_request:
        # Simulate a request failure
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = Exception("Bad Request")
        mock_request.return_value = mock_response
        
        data = fetcher.fetch_market_data("BTCUSDT")
        assert data is None
        
        # Test retry behavior
        assert mock_request.call_count == 3  # Default retry count

def test_authentication(fetcher, mock_response):
    test_api_key = "test_key"
    test_api_secret = "test_secret"
    
    authenticated_fetcher = BinanceFetcher(
        api_key=test_api_key,
        api_secret=test_api_secret
    )
    
    with patch('requests.Session.request') as mock_request:
        mock_response.json.return_value = {"price": "50000.00"}
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        authenticated_fetcher.fetch_market_data("BTCUSDT", "futures")
        
        # Verify API key was included in headers
        call_kwargs = mock_request.call_args[1]
        headers = call_kwargs.get('headers', {})
        assert headers.get('X-MBX-APIKEY') == test_api_key

def test_invalid_market_type(fetcher):
    with pytest.raises(ValueError, match="Invalid market type"):
        fetcher.fetch_market_data("BTCUSDT", "invalid_type")

def test_empty_symbol(fetcher):
    with pytest.raises(ValueError, match="Symbol cannot be empty"):
        fetcher.fetch_market_data("")
