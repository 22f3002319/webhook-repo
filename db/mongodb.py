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
        
        logger.info(f"Initializing MongoDB connection to: {db_name}")
        
        # Create MongoDB client with longer timeout for production
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=30000,  # 30 second timeout
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            retryWrites=True
        )
        
        # Test connection - this will raise if connection fails
        logger.info("Testing MongoDB connection...")
        client.admin.command('ping')
        logger.info("MongoDB ping successful!")
        
        # Get database instance
        db = client[db_name]
        logger.info(f"MongoDB database '{db_name}' accessed successfully")
        
        # Create indexes for better query performance
        try:
            create_indexes(db)
            logger.info("MongoDB indexes created/verified")
        except Exception as index_error:
            logger.warning(f"Index creation failed (may already exist): {index_error}")
        
        logger.info(f"MongoDB client initialized successfully for database: {db_name}")
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection failed: {e}")
        logger.error("Please check:")
        logger.error("1. MongoDB URI is correct")
        logger.error("2. IP address is whitelisted in MongoDB Atlas")
        logger.error("3. Username and password are correct")
        # Reset client and db to None on failure
        client = None
        db = None
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Reset client and db to None on failure
        client = None
        db = None

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
