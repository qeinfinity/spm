from abc import ABC, abstractmethod

class BaseCache(ABC):
    """Abstract base class for caching mechanisms."""
    
    @abstractmethod
    def get(self, key):
        """Retrieve item from cache."""
        pass
    
    @abstractmethod
    def set(self, key, value):
        """Store item in cache."""
        pass
