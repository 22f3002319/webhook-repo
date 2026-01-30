"""
Vercel Serverless Function Entry Point
Adapts Flask app for Vercel's serverless environment
"""

import sys
import os
import traceback

# Add parent directory to path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Import the Flask app WSGI application
    from vercel_app import application
    
    # Vercel Python runtime expects the WSGI application
    # Export it directly
    handler = application
    
except Exception as e:
    # If import fails, create a simple error handler
    def handler(environ, start_response):
        """Error handler if app fails to load"""
        error_msg = f"Error loading application: {str(e)}\n{traceback.format_exc()}"
        status = '500 INTERNAL SERVER ERROR'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [error_msg.encode()]
