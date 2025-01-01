#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import csv
from datetime import datetime
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Configuration
PRICE_HISTORY_FILE = 'price_history.csv'
URL = "https://palmettostatearmory.com/psa-ar-v-16-9mm-1-10-lightweight-m-lok-moe-ept-pistol.html"

def setup_driver():
    """Setup Firefox in headless mode"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Firefox(options=options)

def get_price():
    """Fetch the price using Selenium"""
    driver = None
    try:
        driver = setup_driver()
        driver.get(URL)
        
        wait = WebDriverWait(driver, 10)
        
        # Try different methods to find the price
        try:
            price_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="product:price:amount"]'))
            )
            price = float(price_element.get_attribute('content'))
        except:
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
                    
        if 'price' not in locals():
            raise ValueError("Price element not found")
            
        return price
            
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()

def save_price(price):
    """Save price and timestamp to CSV file"""
    if price is None:
        return
        
    date = datetime.now().strftime('%Y-%m-%d')
    file_exists = os.path.exists(PRICE_HISTORY_FILE)
    
    with open(PRICE_HISTORY_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Price'])
        writer.writerow([date, price])

def load_price_history():
    """Load price history from CSV file"""
    if not os.path.exists(PRICE_HISTORY_FILE):
        return []
        
    with open(PRICE_HISTORY_FILE, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def update_price():
    """Update price data - called by scheduler"""
    price = get_price()
    if price:
        save_price(price)
        print(f"Price updated: ${price}")

# Setup scheduler for daily price updates
scheduler = BackgroundScheduler()
scheduler.add_job(update_price, 'cron', hour=0)  # Run at midnight
scheduler.start()

# Flask routes
@app.route('/')
def index():
    """Render dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/current-price')
def current_price():
    """Get current price"""
    price = get_price()
    return jsonify({'price': price})

@app.route('/api/price-history')
def price_history():
    """Get price history"""
    history = load_price_history()
    return jsonify(history)

# Create templates directory and dashboard.html
os.makedirs('templates', exist_ok=True)
with open('templates/dashboard.html', 'w') as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Price Tracking Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .price-box {
            text-align: center;
            padding: 20px;
            margin-bottom: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .current-price {
            font-size: 2em;
            color: #28a745;
        }
        .chart-container {
            margin-top: 20px;
        }
        h1 {
            text-align: center;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Price Tracking Dashboard</h1>
        <div class="price-box">
            <h2>Current Price</h2>
            <div class="current-price" id="current-price">Loading...</div>
            <div id="last-updated"></div>
        </div>
        <div class="chart-container">
            <canvas id="priceChart"></canvas>
        </div>
    </div>

    <script>
        // Initialize chart
        let chart;
        
        function updateCurrentPrice() {
            fetch('/api/current-price')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('current-price').textContent = 
                        data.price ? `$${data.price.toFixed(2)}` : 'N/A';
                    document.getElementById('last-updated').textContent = 
                        `Last updated: ${new Date().toLocaleString()}`;
                });
        }

        function updateChart() {
            fetch('/api/price-history')
                .then(response => response.json())
                .then(data => {
                    const dates = data.map(item => item.Date);
                    const prices = data.map(item => parseFloat(item.Price));

                    if (chart) {
                        chart.destroy();
                    }

                    const ctx = document.getElementById('priceChart').getContext('2d');
                    chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: dates,
                            datasets: [{
                                label: 'Price History',
                                data: prices,
                                borderColor: '#28a745',
                                tension: 0.1
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Price History Over Time'
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: false,
                                    ticks: {
                                        callback: function(value) {
                                            return '$' + value.toFixed(2);
                                        }
                                    }
                                }
                            }
                        }
                    });
                });
        }

        // Initial load
        updateCurrentPrice();
        updateChart();

        // Refresh data every 5 minutes
        setInterval(updateCurrentPrice, 300000);
        setInterval(updateChart, 300000);
    </script>
</body>
</html>
    """)

if __name__ == "__main__":
    # Create price_history.csv if it doesn't exist
    if not os.path.exists(PRICE_HISTORY_FILE):
        with open(PRICE_HISTORY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Price'])
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)