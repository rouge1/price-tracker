# price-tracker

## The program will:

	1) Fetch the current price from the webpage
	2) Save it to a CSV file (price_history.csv)	
  3) Generate a plot (price_history.png) showing the price trends over time

## Each time it runs, it will:
	1) Add a new row to the CSV with the current date and price
	2) Update the plot with the latest data

## Notes
The script includes error handling for cases where the website 
might be unavailable or the price format changes.
The headers in the request help prevent blocking by the website.
