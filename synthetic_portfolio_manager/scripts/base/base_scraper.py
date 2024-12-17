from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    @abstractmethod
    def scrape(self):
        """Scrape and normalize data."""
        pass
