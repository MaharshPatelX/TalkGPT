from pymongo import MongoClient
from config import MONGODB_URL, DATABASE_NAME
import logging

logger = logging.getLogger(__name__)

# Global database connection
client = None
db = None

def connect_database():
    """Connect to MongoDB"""
    global client, db
    try:
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Test connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

def create_indexes():
    """Create necessary database indexes"""
    try:
        # Sessions collection indexes
        db.sessions.create_index("session_id", unique=True)
        
        # Messages collection indexes
        db.messages.create_index([("session_id", 1), ("sequence_number", 1)])
        db.messages.create_index([("session_id", 1), ("created_at", -1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

def get_database():
    """Get database instance"""
    return db

def close_database():
    """Close database connection"""
    if client:
        client.close()
        logger.info("Database connection closed")