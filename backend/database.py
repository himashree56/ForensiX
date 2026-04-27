"""
MongoDB Database Configuration
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "deepfake_detector")

# Global database client
client: Optional[AsyncIOMotorClient] = None
database = None


async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, database
    try:
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        database = client[DATABASE_NAME]
        # Test connection
        await client.admin.command('ping')
        print(f"[SUCCESS] Connected to MongoDB at {MONGODB_URL}")
        return True
    except Exception as e:
        print(f"[WARNING] Failed to connect to MongoDB: {e}")
        print("[WARNING] Application will run without history features")
        print("[WARNING] See MONGODB_SETUP.md for MongoDB installation instructions")
        client = None
        database = None
        return False


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


def get_database():
    """Get database instance"""
    return database
