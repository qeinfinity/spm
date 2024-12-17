import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

class BaseCache:
    def __init__(self, cache_dir: str):
        """Initialize cache with directory structure for different data types
        
        Args:
            cache_dir: Base directory for cache
        """
        self.base_dir = Path(cache_dir)
        
        # Create directory structure
        self.data_types = ['market', 'orderbook', 'trade']
        for data_type in self.data_types:
            for subdir in ['raw', 'processed']:
                path = self.base_dir / data_type / subdir
                path.mkdir(parents=True, exist_ok=True)
    
    def save_to_cache(self, data: Dict, filename: str, data_type: str = 'market',
                      is_processed: bool = False) -> None:
        """Save data to cache with metadata
        
        Args:
            data: Data to cache
            filename: Base filename without extension
            data_type: Type of data ('market', 'orderbook', 'trade')
            is_processed: Whether this is processed data
        """
        if data_type not in self.data_types:
            raise ValueError(f"Invalid data type: {data_type}. Must be one of {self.data_types}")
        
        subdir = 'processed' if is_processed else 'raw'
        timestamp = int(time.time() * 1000)
        
        # Add metadata
        cache_data = {
            'data': data,
            'metadata': {
                'timestamp': timestamp,
                'filename': filename,
                'data_type': data_type,
                'is_processed': is_processed,
                'cache_time': datetime.now().isoformat()
            }
        }
        
        # Create filename with timestamp
        path = self.base_dir / data_type / subdir / f"{filename}_{timestamp}.json"
        
        with open(path, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load_from_cache(self, filename_pattern: str, data_type: str = 'market',
                       is_processed: bool = False, n_latest: int = 1,
                       time_range: Optional[tuple[int, int]] = None) -> Union[Dict, List[Dict], None]:
        """Load data from cache, optionally returning multiple entries
        
        Args:
            filename_pattern: Base filename pattern to match
            data_type: Type of data to load
            is_processed: Whether to load from processed directory
            n_latest: Number of latest entries to return (default: 1)
            time_range: Optional tuple of (start_ms, end_ms) to filter by timestamp
            
        Returns:
            Single dict if n_latest=1, list of dicts if n_latest>1, None if not found
        """
        if data_type not in self.data_types:
            raise ValueError(f"Invalid data type: {data_type}")
        
        subdir = 'processed' if is_processed else 'raw'
        cache_dir = self.base_dir / data_type / subdir
        
        # Find matching files
        matching_files = list(cache_dir.glob(f"{filename_pattern}_*.json"))
        if not matching_files:
            return None
            
        # Sort files by timestamp (extracted from filename)
        matching_files.sort(key=lambda x: int(x.stem.split('_')[-1]), reverse=True)
        
        results = []
        for file_path in matching_files:
            try:
                with open(file_path, 'r') as f:
                    cache_data = json.load(f)
                    
                # Apply time range filter if specified
                if time_range:
                    start_ms, end_ms = time_range
                    timestamp = cache_data['metadata']['timestamp']
                    if timestamp < start_ms or timestamp > end_ms:
                        continue
                        
                results.append(cache_data)
                if len(results) == n_latest:
                    break
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error reading cache file {file_path}: {e}")
                continue
                
        if not results:
            return None
            
        return results[0] if n_latest == 1 else results
    
    def clear_old_cache(self, max_age_hours: int = 24, data_type: Optional[str] = None) -> None:
        """Clear cache files older than specified age
        
        Args:
            max_age_hours: Maximum age of cache files in hours
            data_type: Optional specific data type to clear, or None for all
        """
        data_types = [data_type] if data_type else self.data_types
        max_age_ms = max_age_hours * 3600 * 1000
        current_time = int(time.time() * 1000)
        
        for dt in data_types:
            for subdir in ['raw', 'processed']:
                cache_dir = self.base_dir / dt / subdir
                for file_path in cache_dir.glob("*.json"):
                    try:
                        # Extract timestamp from filename
                        timestamp = int(file_path.stem.split('_')[-1])
                        if current_time - timestamp > max_age_ms:
                            file_path.unlink()
                    except (ValueError, IndexError):
                        continue
    
    def get_cache_info(self) -> Dict[str, Dict[str, int]]:
        """Get information about cached data
        
        Returns:
            Dict with counts of files per data type and processing state
        """
        info = {}
        for data_type in self.data_types:
            info[data_type] = {
                'raw': len(list((self.base_dir / data_type / 'raw').glob('*.json'))),
                'processed': len(list((self.base_dir / data_type / 'processed').glob('*.json')))
            }
        return info
