"""
Vercel Serverless Function Entry Point
Adapts Flask app for Vercel's serverless environment
"""

import sys
import os

# Add parent directory to path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the Flask app
from vercel_app import application

# Vercel expects the handler to be named 'handler' or the app itself
# Export the WSGI application
handler = application
