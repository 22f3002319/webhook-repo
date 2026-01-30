"""
Flask Application Entry Point
Main application file that initializes Flask app and registers blueprints
"""

from flask import Flask
from flask_cors import CORS
from config import Config
from db.mongodb import init_mongodb
from utils.logger import setup_logging

# Setup logging
setup_logging()

def create_app():
    """Factory function to create and configure Flask app"""
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config.from_object(Config)
    
    # Enable CORS for frontend requests
    CORS(app)
    
    # Initialize MongoDB connection
    init_mongodb(app)
    
    # Register blueprints
    from routes.webhook_routes import webhook_bp
    from routes.api_routes import api_bp
    
    app.register_blueprint(webhook_bp)
    app.register_blueprint(api_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
