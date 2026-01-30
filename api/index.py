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

# Vercel Python runtime automatically calls the WSGI application
# The application function will be used by Vercel
