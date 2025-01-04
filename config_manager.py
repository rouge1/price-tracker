# config_manager.py

import json
import os
import logging
from datetime import datetime

class ConfigManager:
    """Manages item configurations for price tracking"""
    
    def __init__(self, config_file='data/items_config.json', history_file='data/items_history.json'):
        self.config_file = config_file
        self.history_file = history_file
        self.logger = logging.getLogger(__name__)
        self.ensure_config_files()
        
    def ensure_config_files(self):
        """Create config and history files if they don't exist"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        if not os.path.exists(self.config_file):
            self.save_items([])
        if not os.path.exists(self.history_file):
            self.save_history([])
            
    def load_items(self):
        """Load items configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return []
            
    def load_history(self):
        """Load removed items history from file"""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading history: {e}")
            return []
            
    def save_items(self, items):
        """Save items configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(items, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
            
    def save_history(self, history):
        """Save removed items history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
            return False
            
    def add_item(self, name, url):
        """Add a new item to track"""
        items = self.load_items()
        
        # Check if URL already exists
        if any(item['url'] == url for item in items):
            return False, "URL already being tracked"
            
        # Add new item
        items.append({
            'name': name,
            'url': url
        })
        
        if self.save_items(items):
            return True, "Item added successfully"
        return False, "Error saving item"
        
    def remove_item(self, url):
        """Remove an item from tracking and add to history"""
        items = self.load_items()
        history = self.load_history()
        
        # Find and remove item
        removed_items = [item for item in items if item['url'] == url]
        if not removed_items:
            return False, "Item not found"
            
        removed_item = removed_items[0]
        items = [item for item in items if item['url'] != url]
        
        # Add to history with timestamp
        history_entry = {
            **removed_item,
            'removed_at': datetime.now().isoformat()
        }
        history.append(history_entry)
        
        if self.save_items(items) and self.save_history(history):
            return True, "Item removed successfully"
        return False, "Error removing item"
        
    def restore_item(self, url):
        """Restore an item from history to active tracking"""
        history = self.load_history()
        
        # Find and remove from history
        restored_items = [item for item in history if item['url'] == url]
        if not restored_items:
            return False, "Item not found in history"
            
        restored_item = restored_items[0]
        history = [item for item in history if item['url'] != url]
        
        # Remove timestamp and add back to active items
        restored_item.pop('removed_at', None)
        success, message = self.add_item(restored_item['name'], restored_item['url'])
        
        if success:
            self.save_history(history)
            return True, "Item restored successfully"
        return False, message
        
    def get_items(self):
        """Get all tracked items"""
        return self.load_items()
        
    def get_history(self):
        """Get all removed items"""
        return self.load_history()