import json
import os
from datetime import datetime

class BaseCache:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def save_to_cache(self, data, filename):
        path = os.path.join(self.cache_dir, f"{filename}.json")
        with open(path, "w") as file:
            json.dump(data, file)
        print(f"Data cached to {path}")

    def load_from_cache(self, filename):
        path = os.path.join(self.cache_dir, f"{filename}.json")
        if os.path.exists(path):
            with open(path, "r") as file:
                return json.load(file)
        return None
