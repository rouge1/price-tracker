#tracker.py
from scraper import PriceScraper
from datamanager import PriceDataManager
import logging

class PriceTracker:
    """Coordinates price scraping and data management"""
    
    def __init__(self, url, filename):
        self.scraper = PriceScraper(url)
        self.data_manager = PriceDataManager(filename)
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def update_price(self):
        """Update price data"""
        try:
            price = self.scraper.get_price()
            if price:
                self.logger.info(f"Got new price: ${price}")
                self.data_manager.save_price(price)
                return price
            else:
                self.logger.warning("Failed to get price")
                return None
        except Exception as e:
            self.logger.error(f"Error in update_price: {e}")
            return None
        
    def get_price_history(self):
        """Get price history"""
        try:
            history = self.data_manager.load_price_history()
            self.logger.info(f"Retrieved {len(history)} price history records")
            return history
        except Exception as e:
            self.logger.error(f"Error getting price history: {e}")
            return []