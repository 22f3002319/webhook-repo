"""
Vercel-Compatible Flask Application
WSGI application wrapper for Vercel serverless functions
"""

from flask import Flask, request as flask_request
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
    try:
        init_mongodb(app)
    except Exception as e:
        print(f"Warning: MongoDB initialization failed: {e}")
        # Continue without MongoDB for now (will fail on actual DB operations)
    
    # Register blueprints
    from routes.webhook_routes import webhook_bp
    from routes.api_routes import api_bp
    
    app.register_blueprint(webhook_bp)
    app.register_blueprint(api_bp)
    
    return app

# Create the app instance
app = create_app()

# WSGI application for Vercel
def application(environ, start_response):
    """WSGI application wrapper for Vercel"""
    return app(environ, start_response)
