from scraper import PriceScraper
from datamanager import PriceDataManager
import logging

class PriceTracker:
    """Coordinates price scraping and data management for multiple items"""
    
    def __init__(self, items_config):
        """
        Initialize with a list of items to track
        items_config: list of dictionaries with 'url' and 'name' keys
        """
        self.items = {}
        self.logger = logging.getLogger(__name__)
        
        for item in items_config:
            scraper = PriceScraper(item['url'])
            data_manager = PriceDataManager(scraper.item_id)
            self.items[scraper.item_id] = {
                'scraper': scraper,
                'data_manager': data_manager,
                'name': item.get('name', 'Unknown Item')
            }
        
    def update_all_prices(self):
        """Update prices for all tracked items"""
        results = {}
        for item_id, item in self.items.items():
            try:
                data = item['scraper'].get_item_data()
                if data:
                    item['data_manager'].save_price(data['price'])
                    item['data_manager'].save_metadata(data)
                    results[item_id] = data
                    self.logger.info(f"Updated item {item_id}")
            except Exception as e:
                self.logger.error(f"Error updating item {item_id}: {e}")
        return results
        
    def update_price(self, item_id):
        """Update price for a specific item"""
        if item_id not in self.items:
            return None
            
        try:
            item = self.items[item_id]
            data = item['scraper'].get_item_data()
            if data:
                item['data_manager'].save_price(data['price'])
                item['data_manager'].save_metadata(data)
                return data
        except Exception as e:
            self.logger.error(f"Error updating item {item_id}: {e}")
        return None
        
    def get_all_items(self):
        """Get current data for all items"""
        results = {}
        for item_id, item in self.items.items():
            try:
                metadata = item['data_manager'].load_metadata()
                price_history = item['data_manager'].load_price_history()
                results[item_id] = {
                    'metadata': metadata,
                    'price_history': price_history,
                    'name': item['name']
                }
            except Exception as e:
                self.logger.error(f"Error getting item {item_id}: {e}")
        return results
        
    def get_item_data(self, item_id):
        """Get data for a specific item"""
        if item_id not in self.items:
            return None
            
        try:
            item = self.items[item_id]
            return {
                'metadata': item['data_manager'].load_metadata(),
                'price_history': item['data_manager'].load_price_history(),
                'name': item['name']
            }
        except Exception as e:
            self.logger.error(f"Error getting item {item_id}: {e}")
            return None