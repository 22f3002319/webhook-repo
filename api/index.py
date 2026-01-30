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

# Import the Flask app WSGI application
from vercel_app import application

# Vercel Python runtime requires a variable named 'handler' or 'app'
# Export the WSGI application as 'handler'
handler = application

# Also export as 'app' for compatibility
app = application
