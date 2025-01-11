#data_manager.py

import csv
import json
from datetime import datetime
import os
import logging

class PriceDataManager:
    """Manages price data storage and retrieval"""
    
    def __init__(self, item_id):
        self.item_id = item_id
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.price_file = f"{self.data_dir}/{item_id}_prices.csv"
        self.metadata_file = f"{self.data_dir}/{item_id}_metadata.json"
        self.logger = logging.getLogger(__name__)
        self.ensure_files_exist()
        
    def ensure_files_exist(self):
        """Create necessary files if they don't exist"""
        try:
            if not os.path.exists(self.price_file):
                with open(self.price_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Date', 'Price'])
                self.logger.info(f"Created new price file: {self.price_file}")
                
            if not os.path.exists(self.metadata_file):
                self.save_metadata({})
                
        except Exception as e:
            self.logger.error(f"Error creating files: {e}")
    
    def save_price(self, price):
        """Save price and timestamp to CSV file"""
        if price is None:
            self.logger.warning("Attempted to save None price value")
            return
            
        try:
            date = datetime.now().strftime('%Y-%m-%d')
            existing_data = self.load_price_history()
            today_entry_exists = any(entry['Date'] == date for entry in existing_data)
            
            if not today_entry_exists:
                with open(self.price_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([date, f"{price:.2f}"])
                self.logger.info(f"Saved new price {price} for date {date}")
                
        except Exception as e:
            self.logger.error(f"Error saving price: {e}")
            
    def save_metadata(self, metadata):
        """Save item metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f)
            self.logger.info(f"Saved metadata for item {self.item_id}")
        except Exception as e:
            self.logger.error(f"Error saving metadata: {e}")
            
    def load_price_history(self):
        """Load price history from CSV file"""
        try:
            if not os.path.exists(self.price_file):
                return []
                
            with open(self.price_file, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
                
        except Exception as e:
            self.logger.error(f"Error loading price history: {e}")
            return []
            
    def load_metadata(self):
        """Load item metadata from JSON file"""
        try:
            if not os.path.exists(self.metadata_file):
                return {}
                
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading metadata: {e}")
            return {}