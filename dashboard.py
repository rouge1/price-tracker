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
             
    def run(self, host='0.0.0.0', port=5000):
        """Run the Flask application"""
        self.app.run(host=host, port=port)