import logging
import os

class Logger:
    def __init__(self, log_name, log_file):
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(
            filename=f"logs/{log_file}",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(log_name)

    def log(self, message, level="info"):
        if level == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)

# Example usage
logger = Logger("BinanceLogger", "api_calls.log")
logger.log("Successfully fetched BTCUSDT data.")
