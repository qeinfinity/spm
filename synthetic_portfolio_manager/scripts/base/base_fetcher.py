from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    """Abstract base class for all fetchers."""
    
    @abstractmethod
    def fetch(self):
        """Fetch data from the API."""
        pass
