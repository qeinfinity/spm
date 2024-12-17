"""Scheduler for periodic API fetches."""

from apscheduler.schedulers.background import BackgroundScheduler

class DataFetchScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def schedule_fetch(self, fetcher, interval_minutes):
        """Schedule periodic data fetches."""
        self.scheduler.add_job(
            fetcher.fetch,
            'interval',
            minutes=interval_minutes
        )
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
