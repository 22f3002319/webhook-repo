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
    try:
        app = Flask(__name__, static_folder='static', static_url_path='')
        app.config.from_object(Config)
        
        # Enable CORS for frontend requests
        CORS(app)
        
        # Initialize MongoDB connection
        # Don't fail on startup if MongoDB is not available
        # Connection will be established on first use
        try:
            init_mongodb(app)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"MongoDB initialization failed: {e}")
            # Continue without MongoDB - connection will be retried on first DB operation
        
        # Register blueprints
        from routes.webhook_routes import webhook_bp
        from routes.api_routes import api_bp
        
        app.register_blueprint(webhook_bp)
        app.register_blueprint(api_bp)
        
        return app
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create Flask app: {e}")
        # Return a minimal error app
        error_app = Flask(__name__)
        @error_app.route('/', defaults={'path': ''})
        @error_app.route('/<path:path>')
        def error_handler(path):
            return f"Application initialization error: {str(e)}", 500
        return error_app

# Create the app instance
# Vercel will automatically convert Flask app to WSGI
app = create_app()
