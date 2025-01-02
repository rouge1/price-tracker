from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import os
import logging
import hashlib

class PriceScraper:
    """Handles web scraping of prices and item details"""
    
    def __init__(self, url):
        self.url = url
        self.item_id = self._generate_item_id(url)
        self.screenshot_dir = "static/thumbnails"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def _generate_item_id(self, url):
        """Generate a unique ID for the item based on URL"""
        return hashlib.md5(url.encode()).hexdigest()[:10]
        
    def setup_driver(self):
        """Setup Firefox in headless mode"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        return webdriver.Firefox(options=options)
        
    def get_item_data(self):
        """Fetch price, title, and thumbnail"""
        driver = None
        try:
            driver = self.setup_driver()
            driver.get(self.url)
            wait = WebDriverWait(driver, 10)
            
            # Get price
            price = self._get_price(wait)
            
            # Get title
            title = self._get_title(wait)
            
            # Take screenshot if not exists
            thumbnail_path = self._get_or_create_thumbnail(driver)
            
            return {
                'item_id': self.item_id,
                'price': price,
                'title': title,
                'url': self.url,
                'thumbnail_path': thumbnail_path
            }
                
        except Exception as e:
            self.logger.error(f"Error fetching item data: {e}")
            return None
            
        finally:
            if driver:
                driver.quit()
                
    def _get_price(self, wait):
        """Extract price from page"""
        try:
            price_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="product:price:amount"]'))
            )
            return float(price_element.get_attribute('content'))
        except:
            # Try alternative selectors
            selectors = ['.price', '.regular-price', 'span[data-price-type="finalPrice"]', '.product-price']
            for selector in selectors:
                try:
                    price_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    price_text = price_element.text or price_element.get_attribute('content')
                    if price_text:
                        return float(price_text.replace('$', '').replace(',', '').strip())
                except:
                    continue
            raise ValueError("Price not found")
            
    def _get_title(self, wait):
        """Extract title from page"""
        try:
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="og:title"]'))
            )
            return title_element.get_attribute('content')
        except:
            try:
                title_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.page-title'))
                )
                return title_element.text.strip()
            except:
                return "Unknown Title"
                
    def _get_or_create_thumbnail(self, driver):
        """Get existing thumbnail or create new one"""
        thumbnail_path = f"{self.screenshot_dir}/{self.item_id}.png"
        
        if not os.path.exists(thumbnail_path):
            try:
                # Ensure the product image is in view
                driver.execute_script("window.scrollTo(0, 0)")
                driver.save_screenshot(thumbnail_path)
                self.logger.info(f"Created new thumbnail: {thumbnail_path}")
            except Exception as e:
                self.logger.error(f"Error creating thumbnail: {e}")
                return None
                
        return thumbnail_path