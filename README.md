# Price Tracker
A web-based tool that tracks product prices across various websites and visualizes price history over time. Built with Python, Flask, and Selenium.

# Features

	Automated price tracking for multiple products
	Daily price updates with configurable schedules
	Interactive dashboard to monitor price trends
	Product thumbnail capture and storage
	Price history visualization
	Easy product addition and removal
	Removed items history with restore capability

# Requirements

	Python 3.x
	Firefox Browser (for Selenium WebDriver)

# Required Python packages:
	Flask
	Selenium
	APScheduler
	logging

# Quick Start

1. Clone the repository
2. Install dependencies:

		bash pip install Flask Selenium APScheduler logging

3. Run the application:

		bash python main.py

4. Access the dashboard at http://localhost:5000

# Project Structure

	main.py - Application entry point
	dashboard.py - Web interface and API endpoints
	tracker.py - Core price tracking functionality
	scraper.py - Web scraping implementation
	datamanager.py - Data storage and retrieval
	config_manager.py - Configuration management

# Data Storage
The application stores data in the following directories:

	/data - Price histories and metadata
	/static/thumbnails - Product images
	/templates - Dashboard HTML templates

# Contributing
Feel free to open issues or submit pull requests with improvements.
# Note
This tool is intended for personal use and educational purposes. Please respect websites' terms of service and implement appropriate rate limiting when scraping.
