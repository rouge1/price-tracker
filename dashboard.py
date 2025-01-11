from flask import Flask, render_template, jsonify, send_from_directory, request, Response
from apscheduler.schedulers.background import BackgroundScheduler
import json
#import os
import time

class Dashboard:
    """Flask application for the dashboard"""
    
    def __init__(self, tracker, config_manager):
        self.app = Flask(__name__, static_folder='static')
        self.tracker = tracker
        self.config_manager = config_manager
        self.setup_routes()
        self.setup_scheduler()
        
    def setup_scheduler(self):
        """Setup automated price updates"""
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.tracker.update_all_prices, 'cron', hour=0)
        scheduler.start()

    def setup_routes(self):
        """Setup Flask routes"""
        
        def generate_status():
            # Capture config_manager reference
            config_manager = self.config_manager
            while True:
                # Get latest status for all items
                config_items = config_manager.get_items()
                statuses = {item['url']: item.get('status', 'checking') 
                        for item in config_items}
                
                # Format as SSE data
                data = f"data: {json.dumps(statuses)}\n\n"
                yield data
                time.sleep(1)  # Check every second
        
        @self.app.route('/')
        def index():
            return render_template('dashboard.html')
    
        @self.app.route('/api/status/stream')
        def status_stream_endpoint():
            """SSE endpoint for status updates"""
            return Response(
                generate_status(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            )
                
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
            
        @self.app.route('/api/history')
        def get_history():
            """Get history of removed items"""
            return jsonify(self.config_manager.get_history())
            
        @self.app.route('/api/history/restore', methods=['POST'])
        def restore_item():
            """Restore an item from history"""
            data = request.json
            success, message = self.config_manager.restore_item(data['url'])
            if success:
                # Reinitialize tracker with new configuration
                items = self.config_manager.get_items()
                self.tracker.update_configuration(items)
                # Update prices immediately for the restored item
                self.tracker.update_all_prices()
            return jsonify({'success': success, 'message': message})
            
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory('static', filename)
        
        @self.app.route('/api/status')
        def get_status():
            """Get current status of all items"""
            statuses = {}
            for item_id, item in self.tracker.items.items():
                try:
                    metadata = item['data_manager'].load_metadata()
                    if metadata and metadata.get('last_update'):
                        status = 'success'
                    else:
                        status = 'checking'
                    statuses[item['scraper'].url] = status
                except Exception as e:
                    statuses[item['scraper'].url] = 'error'
            return jsonify(statuses)
            
        @self.app.route('/api/status/stream')
        def stream_status():
            """SSE endpoint for status updates"""
            def generate_status():
                while True:
                    # Get latest status for all items
                    config_items = self.config_manager.get_items()
                    statuses = {item['url']: item.get('status', 'checking') 
                            for item in config_items}
                    
                    # Format as SSE data
                    data = f"data: {json.dumps(statuses)}\n\n"
                    yield data
                    time.sleep(1)  # Check every second

            return Response(
                generate_status(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            )            

    def run(self, host='0.0.0.0', port=5000):
        """Run the Flask application"""
        self.app.run(host=host, port=port)