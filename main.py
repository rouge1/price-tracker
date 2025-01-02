#!/usr/bin/env python3
from tracker import PriceTracker
from dashboard import Dashboard
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
    
    # Configure items to track
    items_config = [
        {
            'name': 'PSA AR-V 9mm Pistol',
            'url': "https://palmettostatearmory.com/psa-ar-v-16-9mm-1-10-lightweight-m-lok-moe-ept-pistol.html"
        }
        # Add more items here as needed
        # {
        #     'name': 'Another Item',
        #     'url': 'https://example.com/another-item'
        # }
    ]
    
    # Initialize components
    tracker = PriceTracker(items_config)
    
    # Initial price update
    logging.info("Performing initial price update...")
    tracker.update_all_prices()
    
    # Initialize and run dashboard
    dashboard = Dashboard(tracker)
    dashboard.run()

if __name__ == "__main__":
    main()