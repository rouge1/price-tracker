#scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

class PriceScraper:
    """Handles web scraping of prices"""
    
    def __init__(self, url):
        self.url = url
        
    def setup_driver(self):
        """Setup Firefox in headless mode"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Firefox(options=options)
        
    def get_price(self):
        """Fetch the price using Selenium"""
        driver = None
        try:
            driver = self.setup_driver()
            driver.get(self.url)
            
            wait = WebDriverWait(driver, 10)
            
            # Try meta tag first
            try:
                price_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="product:price:amount"]'))
                )
                price = float(price_element.get_attribute('content'))
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
                            price = float(price_text.replace('$', '').replace(',', '').strip())
                            break
                    except:
                        continue
                        
            if 'price' not in locals():
                raise ValueError("Price element not found")
                
            return price
                
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
            
        finally:
            if driver:
                driver.quit()