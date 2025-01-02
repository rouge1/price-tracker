#!/usr/bin/env python3
from tracker import PriceTracker
from dashboard import Dashboard
import logging

def test_price_tracking(tracker):
    """Test price tracking functionality"""
    logging.info("Testing price tracking...")
    
    # Test getting and saving price
    price = tracker.update_price()
    if price:
        logging.info(f"Successfully got and saved price: ${price}")
    else:
        logging.error("Failed to get price")
        
    # Test loading price history
    history = tracker.get_price_history()
    logging.info(f"Loaded {len(history)} price records")
    for record in history:
        logging.info(f"Record: Date={record['Date']}, Price=${record['Price']}")

def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    URL = "https://palmettostatearmory.com/psa-ar-v-16-9mm-1-10-lightweight-m-lok-moe-ept-pistol.html"
    PRICE_HISTORY_FILE = 'price_history.csv'
    
    # Initialize components
    tracker = PriceTracker(URL, PRICE_HISTORY_FILE)
    
    # Run test
    test_price_tracking(tracker)
    
    # Initialize and run dashboard
    dashboard = Dashboard(tracker)
    dashboard.run()

if __name__ == "__main__":
    main()