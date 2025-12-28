"""
Database Configuration
"""
from pymongo import MongoClient
from constants import Config

# Initialize MongoDB connection
client = MongoClient(Config.MONGO_URI)
db = client[Config.DATABASE_NAME]


def get_db():
    """Get database instance"""
    return db


def close_db():
    """Close database connection"""
    client.close()