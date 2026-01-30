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
        mongodb_uri = app.config['MONGODB_URI']
        db_name = app.config['MONGODB_DB_NAME']
        
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        
        # Create MongoDB client
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Test connection
        client.admin.command('ping')
        
        # Get database instance
        db = client[db_name]
        
        # Create indexes for better query performance
        create_indexes(db)
        
        logger.info(f"Successfully connected to MongoDB Atlas: {db_name}")
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {e}")
        raise
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {e}")
        raise

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
    if db is None:
        raise RuntimeError("Database not initialized. Call init_mongodb() first.")
    return db

def close_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")
