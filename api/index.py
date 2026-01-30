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

# Import the Flask app directly
from vercel_app import app

# Vercel Python runtime requires a variable named 'handler' or 'app'
# Export the Flask app directly - Vercel will handle WSGI conversion
handler = app
