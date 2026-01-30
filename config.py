"""
Configuration Settings
Centralized configuration management using environment variables
"""

import os
from datetime import timedelta

class Config:
    """Application configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MongoDB Atlas settings
    MONGODB_URI = os.environ.get('MONGODB_URI') or ''
    # Replace URL-encoded characters if needed
    if MONGODB_URI:
        MONGODB_URI = MONGODB_URI.replace('%23', '#')  # Decode # from URL encoding
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME') or 'github_webhooks'
    
    # GitHub Webhook settings
    GITHUB_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET') or ''
    
    # Application settings
    POLLING_INTERVAL = 15  # seconds (for frontend polling)
