"""
Vercel Serverless Function Entry Point
Adapts Flask app for Vercel's serverless environment
"""

import sys
import os

# Add parent directory to path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the Flask app
from vercel_app import app

# Create a WSGI handler function that Vercel can recognize
# Vercel expects a callable function, not the app object directly
def handler(environ, start_response):
    """
    WSGI handler function for Vercel
    Wraps the Flask app to work with Vercel's Python runtime
    """
    return app(environ, start_response)

# Also export app for compatibility
# But handler takes precedence
