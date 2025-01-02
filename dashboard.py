from flask import Flask, render_template, jsonify, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
import os

class Dashboard:
    """Flask application for the dashboard"""
    
    def __init__(self, tracker):
        self.app = Flask(__name__, static_folder='static')
        self.tracker = tracker
        self.setup_routes()
        self.setup_scheduler()
        self.create_template()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('dashboard.html')
            
        @self.app.route('/api/items')
        def get_items():
            """Get all items data"""
            return jsonify(self.tracker.get_all_items())
            
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory('static', filename)
            
    def setup_scheduler(self):
        """Setup automated price updates"""
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.tracker.update_all_prices, 'cron', hour=0)
        scheduler.start()
        
    def create_template(self):
        """Create dashboard HTML template"""
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
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .items-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .item-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
        }
        .item-title {
            font-size: 1.2em;
            margin: 0 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .item-title a {
            color: #0066cc;
            text-decoration: none;
        }
        .item-title a:hover {
            text-decoration: underline;
        }
        .item-content {
            display: flex;
            gap: 20px;
        }
        .item-left {
            flex: 0 0 auto;
            width: 200px;
        }
        .item-right {
            flex: 1;
            min-width: 0;
        }
        .thumbnail {
            width: 200px;
            height: 200px;
            object-fit: cover;
            border-radius: 5px;
        }
        .chart-container {
            height: 200px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Price Tracking Dashboard</h1>
        <div class="items-list" id="items-container">
            <!-- Items will be dynamically inserted here -->
        </div>
    </div>

    <script>
        // Store charts by item ID
        const charts = {};
        
        function createItemCard(itemId, data) {
            const metadata = data.metadata;
            const history = data.price_history;
            
            const card = document.createElement('div');
            card.className = 'item-card';
            
            // Title at the top
            const title = document.createElement('h2');
            title.className = 'item-title';
            const titleLink = document.createElement('a');
            titleLink.href = metadata.url;
            titleLink.target = '_blank';
            titleLink.textContent = metadata.title;
            title.appendChild(titleLink);
            card.appendChild(title);
            
            // Content container
            const content = document.createElement('div');
            content.className = 'item-content';
            
            // Left side with thumbnail
            const leftSide = document.createElement('div');
            leftSide.className = 'item-left';
            
            const thumbnail = document.createElement('img');
            thumbnail.className = 'thumbnail';
            thumbnail.src = metadata.thumbnail_path || '/static/placeholder.png';
            thumbnail.alt = metadata.title;
            leftSide.appendChild(thumbnail);
            
            content.appendChild(leftSide);
            
            // Right side with chart
            const rightSide = document.createElement('div');
            rightSide.className = 'item-right';
            
            const chartContainer = document.createElement('div');
            chartContainer.className = 'chart-container';
            const canvas = document.createElement('canvas');
            chartContainer.appendChild(canvas);
            rightSide.appendChild(chartContainer);
            
            content.appendChild(rightSide);
            card.appendChild(content);
            
            // Create chart
            const dates = history.map(item => item.Date);
            const prices = history.map(item => parseFloat(item.Price));
            
            const ctx = canvas.getContext('2d');
            charts[itemId] = new Chart(ctx, {
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
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `$${context.raw.toFixed(2)}`;
                                }
                            }
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
            
            return card;
        }
        
        function updateDashboard() {
            fetch('/api/items')
                .then(response => response.json())
                .then(items => {
                    const container = document.getElementById('items-container');
                    container.innerHTML = '';
                    
                    for (const [itemId, data] of Object.entries(items)) {
                        const card = createItemCard(itemId, data);
                        container.appendChild(card);
                    }
                });
        }

        // Initial load
        updateDashboard();

        // Refresh every 5 minutes
        setInterval(updateDashboard, 300000);
    </script>
</body>
</html>
            """)
            
    def run(self, host='0.0.0.0', port=5000):
        """Run the Flask application"""
        self.app.run(host=host, port=port)