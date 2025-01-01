#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import os
import time

def setup_driver():
    """Setup Firefox in headless mode"""
    options = Options()
    options.add_argument('--headless')  # Run in headless mode (no GUI)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Firefox(options=options)

def get_price(url):
    """Fetch the price using Selenium"""
    driver = None
    try:
        print("Starting browser...")
        driver = setup_driver()
        
        print("Accessing website...")
        driver.get(url)
        
        # Wait up to 10 seconds for the price element to be present
        wait = WebDriverWait(driver, 10)
        
        # Try different methods to find the price
        price_element = None
        try:
            # Try meta tag first
            price_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="product:price:amount"]'))
            )
            price = float(price_element.get_attribute('content'))
        except:
            # If meta tag fails, try other common price elements
            print("Meta tag not found, trying alternative selectors...")
            selectors = [
                '.price',
                '.regular-price',
                'span[data-price-type="finalPrice"]',
                '.product-price'
            ]
            for selector in selectors:
                try:
                    price_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    price_text = price_element.text or price_element.get_attribute('content')
                    if price_text:
                        price = float(price_text.replace('$', '').replace(',', '').strip())
                        break
                except:
                    continue
        
        if price_element is None:
            raise ValueError("Price element not found")
            
        print(f"Successfully found price: ${price}")
        return price
            
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()

def save_price(price, filename='price_history.csv'):
    """Save price and timestamp to CSV file"""
    date = datetime.now().strftime('%Y-%m-%d')
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Price'])
        writer.writerow([date, price])
    print(f"Price saved to {filename}")

def plot_prices(filename='price_history.csv'):
    """Create a price history plot"""
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            dates, prices = zip(*[(row[0], float(row[1])) for row in reader])

        plt.figure(figsize=(12, 6))
        plt.plot(dates, prices, marker='o')
        plt.title('Price History Over Time')
        plt.xlabel('Date')
        plt.ylabel('Price ($)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('price_history.png')
        plt.close()
        print("Price history plot saved as price_history.png")
        
    except Exception as e:
        print(f"Error creating plot: {e}")

def main():
    url = "https://palmettostatearmory.com/psa-ar-v-16-9mm-1-10-lightweight-m-lok-moe-ept-pistol.html"
    print(f"Fetching price from {url}")
    price = get_price(url)
    
    if price:
        print(f"Current price: ${price}")
        save_price(price)
        plot_prices()
    else:
        print("Failed to fetch price")

if __name__ == "__main__":
    main()