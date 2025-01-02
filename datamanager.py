#datamnager.py
import csv
from datetime import datetime
import os
import logging

class PriceDataManager:
    """Manages price data storage and retrieval"""
    
    def __init__(self, filename):
        self.filename = filename
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.ensure_file_exists()
        
    def ensure_file_exists(self):
        """Create price history file if it doesn't exist"""
        try:
            if not os.path.exists(self.filename):
                with open(self.filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Date', 'Price'])
                self.logger.info(f"Created new price history file: {self.filename}")
        except Exception as e:
            self.logger.error(f"Error creating price history file: {e}")
    
    def save_price(self, price):
        """Save price and timestamp to CSV file"""
        if price is None:
            self.logger.warning("Attempted to save None price value")
            return
            
        try:
            date = datetime.now().strftime('%Y-%m-%d')
            
            # Check if we already have an entry for today
            existing_data = self.load_price_history()
            today_entry_exists = any(entry['Date'] == date for entry in existing_data)
            
            if not today_entry_exists:
                with open(self.filename, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([date, f"{price:.2f}"])
                self.logger.info(f"Saved new price {price} for date {date}")
            else:
                self.logger.info(f"Price for {date} already exists")
                
        except Exception as e:
            self.logger.error(f"Error saving price: {e}")
            
    def load_price_history(self):
        """Load price history from CSV file"""
        try:
            if not os.path.exists(self.filename):
                self.logger.warning("Price history file not found")
                return []
                
            with open(self.filename, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
                self.logger.info(f"Loaded {len(data)} price records")
                return data
                
        except Exception as e:
            self.logger.error(f"Error loading price history: {e}")
            return []