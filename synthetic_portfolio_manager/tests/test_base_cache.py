import pytest
import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from scripts.base.base_cache import BaseCache

@pytest.fixture
def temp_cache_dir(tmp_path):
    return str(tmp_path / "test_cache")

@pytest.fixture
def cache(temp_cache_dir):
    return BaseCache(temp_cache_dir)

def test_directory_structure_creation(temp_cache_dir):
    cache = BaseCache(temp_cache_dir)
    
    # Check main directories
    for data_type in ['market', 'orderbook', 'trade']:
        for subdir in ['raw', 'processed']:
            path = Path(temp_cache_dir) / data_type / subdir
            assert path.exists()
            assert path.is_dir()

def test_save_and_load_market_data(cache):
    test_data = {
        "symbol": "BTCUSDT",
        "price": 50000.00,
        "timestamp": int(time.time() * 1000)
    }
    
    # Save data
    cache.save_to_cache(test_data, "btc_market", "market", is_processed=True)
    
    # Load data
    loaded_data = cache.load_from_cache("btc_market", "market", is_processed=True)
    
    assert loaded_data is not None
    assert loaded_data['data'] == test_data
    assert 'metadata' in loaded_data
    assert loaded_data['metadata']['data_type'] == 'market'
    assert loaded_data['metadata']['is_processed'] == True

def test_load_multiple_versions(cache):
    # Save multiple versions of the same data
    for i in range(3):
        test_data = {"version": i, "timestamp": int(time.time() * 1000)}
        time.sleep(0.1)  # Ensure different timestamps
        cache.save_to_cache(test_data, "test_data", "market")
    
    # Load latest 2 versions
    loaded_data = cache.load_from_cache("test_data", "market", n_latest=2)
    
    assert isinstance(loaded_data, list)
    assert len(loaded_data) == 2
    assert loaded_data[0]['data']['version'] == 2  # Latest version
    assert loaded_data[1]['data']['version'] == 1  # Second latest

def test_time_range_filtering(cache):
    current_time = int(time.time() * 1000)
    
    # Save data with different timestamps
    for i in range(3):
        test_data = {"version": i}
        cache.save_to_cache(
            test_data,
            "time_test",
            "market",
            timestamp=current_time - (i * 3600 * 1000)  # 1 hour intervals
        )
    
    # Load data within specific time range
    time_range = (current_time - 7200000, current_time)  # Last 2 hours
    loaded_data = cache.load_from_cache(
        "time_test",
        "market",
        time_range=time_range,
        n_latest=10
    )
    
    assert isinstance(loaded_data, list)
    assert len(loaded_data) == 2  # Should only get data from last 2 hours

def test_clear_old_cache(cache):
    current_time = int(time.time() * 1000)
    
    # Save data with different ages
    test_data = {"data": "recent"}
    old_data = {"data": "old"}
    
    cache.save_to_cache(test_data, "recent_data", "market")
    
    # Save old data with timestamp 25 hours ago
    cache.save_to_cache(
        old_data,
        "old_data",
        "market",
        timestamp=current_time - (25 * 3600 * 1000)
    )
    
    # Clear cache older than 24 hours
    cache.clear_old_cache(max_age_hours=24)
    
    # Check that old data is gone but recent data remains
    assert cache.load_from_cache("old_data", "market") is None
    assert cache.load_from_cache("recent_data", "market") is not None

def test_invalid_data_type(cache):
    test_data = {"test": "data"}
    
    with pytest.raises(ValueError, match="Invalid data type"):
        cache.save_to_cache(test_data, "test", "invalid_type")
        
    with pytest.raises(ValueError, match="Invalid data type"):
        cache.load_from_cache("test", "invalid_type")

def test_metadata_validation(cache):
    test_data = {"test": "data"}
    timestamp = int(time.time() * 1000)
    
    cache.save_to_cache(test_data, "metadata_test", "market")
    loaded_data = cache.load_from_cache("metadata_test", "market")
    
    metadata = loaded_data['metadata']
    assert 'timestamp' in metadata
    assert 'filename' in metadata
    assert 'data_type' in metadata
    assert 'is_processed' in metadata
    assert 'cache_time' in metadata
    
    assert metadata['filename'] == 'metadata_test'
    assert metadata['data_type'] == 'market'
    assert isinstance(metadata['timestamp'], int)
    assert isinstance(metadata['is_processed'], bool)

def test_cache_info(cache):
    # Save some test data
    test_data = {"test": "data"}
    cache.save_to_cache(test_data, "info_test1", "market", is_processed=False)
    cache.save_to_cache(test_data, "info_test2", "market", is_processed=True)
    cache.save_to_cache(test_data, "info_test3", "orderbook", is_processed=False)
    
    info = cache.get_cache_info()
    
    assert 'market' in info
    assert 'orderbook' in info
    assert 'trade' in info
    assert info['market']['raw'] == 1
    assert info['market']['processed'] == 1
    assert info['orderbook']['raw'] == 1
    assert info['orderbook']['processed'] == 0

def test_file_corruption_handling(cache):
    # Save valid data
    test_data = {"test": "data"}
    cache.save_to_cache(test_data, "valid_data", "market")
    
    # Corrupt the file
    cache_file = next(Path(cache.base_dir / 'market' / 'raw').glob("valid_data_*.json"))
    with open(cache_file, 'w') as f:
        f.write("corrupted json data")
    
    # Should handle corrupted file gracefully
    loaded_data = cache.load_from_cache("valid_data", "market")
    assert loaded_data is None