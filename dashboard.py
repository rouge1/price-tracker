from flask import Flask, render_template, jsonify, send_from_directory, request
from apscheduler.schedulers.background import BackgroundScheduler
import os

class Dashboard:
    """Flask application for the dashboard"""
    
    def __init__(self, tracker, config_manager):
        self.app = Flask(__name__, static_folder='static')
        self.tracker = tracker
        self.config_manager = config_manager
        self.setup_routes()
        self.setup_scheduler()
        self.create_template()
        
    def setup_scheduler(self):
        """Setup automated price updates"""
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.tracker.update_all_prices, 'cron', hour=0)
        scheduler.start()

    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('dashboard.html')
            
        @self.app.route('/api/items')
        def get_items():
            """Get all items data"""
            return jsonify(self.tracker.get_all_items())
            
        @self.app.route('/api/config/items')
        def get_config_items():
            """Get items configuration"""
            return jsonify(self.config_manager.get_items())
            
        @self.app.route('/api/config/add', methods=['POST'])
        def add_item():
            """Add new item to track"""
            data = request.json
            success, message = self.config_manager.add_item(data['name'], data['url'])
            if success:
                # Reinitialize tracker with new configuration
                items = self.config_manager.get_items()
                self.tracker.update_configuration(items)
                # Update prices immediately for the new item
                self.tracker.update_all_prices()
            return jsonify({'success': success, 'message': message})
            
        @self.app.route('/api/config/remove', methods=['POST'])
        def remove_item():
            """Remove item from tracking"""
            data = request.json
            success, message = self.config_manager.remove_item(data['url'])
            if success:
                # Reinitialize tracker with new configuration
                items = self.config_manager.get_items()
                self.tracker.update_configuration(items)
                # Update prices immediately for the new item
                #self.tracker.update_all_prices()
            return jsonify({'success': success, 'message': message})
            
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory('static', filename)
            
    def create_template(self):
        """Create dashboard HTML template"""
        os.makedirs('templates', exist_ok=True)
        with open('templates/dashboard.html', 'w') as f:
            f.write('''<!DOCTYPE html>
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
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border: 1px solid transparent;
            border-bottom: none;
            margin-bottom: -1px;
        }
        .tab.active {
            background-color: white;
            border-color: #ddd;
            border-bottom-color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .config-form {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .config-form input[type="text"] {
            width: 100%;
            padding: 8px;
            margin: 5px 0 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .config-form button {
            background-color: #28a745;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .config-form button:hover {
            background-color: #218838;
        }
        .config-list {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
        }
        .config-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .config-item:last-child {
            border-bottom: none;
        }
        .remove-btn {
            background-color: #dc3545;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .remove-btn:hover {
            background-color: #c82333;
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
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('tracking')">Price Tracking</div>
            <div class="tab" onclick="switchTab('config')">Configuration</div>
        </div>
        
        <div id="tracking-tab" class="tab-content active">
            <div class="items-list" id="items-container">
                <!-- Items will be dynamically inserted here -->
            </div>
        </div>
        
        <div id="config-tab" class="tab-content">
            <div class="config-form">
                <h2>Add New Item to Track</h2>
                <form id="add-item-form" onsubmit="return addItem(event)">
                    <div>
                        <label for="item-name">Item Name:</label>
                        <input type="text" id="item-name" required>
                    </div>
                    <div>
                        <label for="item-url">Item URL:</label>
                        <input type="text" id="item-url" required>
                    </div>
                    <button type="submit">Add Item</button>
                </form>
            </div>
            
            <div class="config-list" id="config-items">
                <!-- Configuration items will be dynamically inserted here -->
            </div>
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
        
        function switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelector(`.tab[onclick="switchTab('${tabName}')"]`).classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Refresh content if needed
            if (tabName === 'tracking') {
                updateDashboard();
            } else if (tabName === 'config') {
                updateConfigList();
            }
        }
        
        function updateConfigList() {
            fetch('/api/config/items')
                .then(response => response.json())
                .then(items => {
                    const container = document.getElementById('config-items');
                    container.innerHTML = '<h2>Currently Tracked Items</h2>';
                    
                    items.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'config-item';
                        div.innerHTML = `
                            <div>
                                <strong>${item.name}</strong><br>
                                <small>${item.url}</small>
                            </div>
                            <button class="remove-btn" onclick="removeItem('${item.url}')">Remove</button>
                        `;
                        container.appendChild(div);
                    });
                });
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
        
        function addItem(event) {
            event.preventDefault();
            const name = document.getElementById('item-name').value;
            const url = document.getElementById('item-url').value;
            
            fetch('/api/config/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, url }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('add-item-form').reset();
                    updateConfigList();
                    updateDashboard();
                }
                alert(data.message);
            });
            
            return false;
        }
        
        function removeItem(url) {
            if (confirm('Are you sure you want to remove this item?')) {
                fetch('/api/config/remove', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateConfigList();
                        updateDashboard();
                    }
                    alert(data.message);
                });
            }
        }

        // Initial load
        updateDashboard();
        
    </script>
</body>
</html>''')
            
    def run(self, host='0.0.0.0', port=5000):
        """Run the Flask application"""
        self.app.run(host=host, port=port)