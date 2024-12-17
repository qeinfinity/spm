import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

def setup_logging(log_dir: str = 'logs', level: int = logging.INFO) -> None:
    """Set up logging configuration for the application
    
    Args:
        log_dir: Directory to store log files
        level: Logging level (default: INFO)
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamp for log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'spm_{timestamp}.log'
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set up specific loggers for main components
    components = ['fetcher', 'processor', 'cache']
    for component in components:
        logger = logging.getLogger(f'spm.{component}')
        logger.setLevel(level)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name
    
    Args:
        name: Logger name (will be prefixed with 'spm.')
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f'spm.{name}')
