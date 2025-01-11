#!/usr/bin/env python3
#main.py

from tracker import PriceTracker
from dashboard import Dashboard
from config_manager import ConfigManager  # Ensure this import is correct
import logging
import os

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('price_tracker.log')
        ]
    )

def ensure_directories():
    """Ensure required directories exist"""
    directories = ['static', 'static/thumbnails', 'data', 'templates']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main entry point"""
    # Setup
    setup_logging()
    ensure_directories()
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Initialize components
    items_config = config_manager.get_items()  # Ensure this returns the correct structure
    tracker = PriceTracker(items_config, config_manager)
    
    # Initial price update
    logging.info("Performing initial price update...")
    tracker.update_all_prices()
    
    # Initialize and run dashboard
    dashboard = Dashboard(tracker, config_manager)
    dashboard.run()

if __name__ == "__main__":
    main()