"""
MongoDB Connection and Database Utilities
Handles MongoDB Atlas connection and provides database access
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)

# Global MongoDB client instance
client = None
db = None

def init_mongodb(app):
    """
    Initialize MongoDB connection using Flask app configuration
    
    Args:
        app: Flask application instance
    """
    global client, db
    
    try:
        mongodb_uri = app.config.get('MONGODB_URI', '')
        db_name = app.config.get('MONGODB_DB_NAME', 'github_webhooks')
        
        if not mongodb_uri:
            logger.warning("MONGODB_URI environment variable is not set. MongoDB features will be unavailable.")
            return  # Don't raise error, allow app to start
        
        # Create MongoDB client with longer timeout for serverless
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=10000,  # 10 second timeout for serverless
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            retryWrites=True
        )
        
        # Test connection (non-blocking for serverless)
        try:
            client.admin.command('ping')
        except Exception as ping_error:
            logger.warning(f"MongoDB ping failed: {ping_error}. Connection will be retried on first use.")
            # Don't raise - allow lazy connection
        
        # Get database instance
        db = client[db_name]
        
        # Create indexes for better query performance (non-blocking)
        try:
            create_indexes(db)
        except Exception as index_error:
            logger.warning(f"Index creation failed (may already exist): {index_error}")
        
        logger.info(f"MongoDB client initialized for database: {db_name}")
        
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {e}")
        # Don't raise - allow app to start without MongoDB
        # Connection will be retried on first DB operation

def create_indexes(db_instance):
    """
    Create database indexes for optimized queries
    
    Args:
        db_instance: MongoDB database instance
    """
    try:
        # Index on timestamp for efficient sorting and filtering
        db_instance.events.create_index([("timestamp", -1)])
        
        # Index on request_id to prevent duplicates
        db_instance.events.create_index([("request_id", 1)], unique=True)
        
        # Compound index for author and timestamp queries
        db_instance.events.create_index([("author", 1), ("timestamp", -1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Error creating indexes (may already exist): {e}")

def get_db():
    """
    Get the database instance
    
    Returns:
        MongoDB database instance
    """
    global db
    if db is None:
        # Try to initialize if not already done
        try:
            from flask import current_app
            if current_app:
                init_mongodb(current_app)
        except Exception:
            pass
        
        if db is None:
            raise RuntimeError("Database not initialized. Call init_mongodb() first.")
    return db

def close_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")
