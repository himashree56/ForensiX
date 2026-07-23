"""
MongoDB Database Configuration
"""
import os
import asyncio
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
        import certifi
        client = AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsCAFile=certifi.where(),
        )
        database = client[DATABASE_NAME]
        # Test connection
        await client.admin.command('ping')
        print(f"[SUCCESS] Connected to MongoDB at {MONGODB_URL}")
        return True
    except Exception as e:
        print(f"[WARNING] Failed to connect to MongoDB: {e}")
        print("[WARNING] Application will run without history/auth features")
        client = None
        database = None
        return False


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


async def ensure_connected() -> bool:
    """Try to reconnect if not connected."""
    global client, database
    if database is not None:
        try:
            await client.admin.command('ping')
            return True
        except Exception:
            pass  # Fall through to reconnect
    return await connect_to_mongo()


def get_database():
    """Get database instance — raises 503 if MongoDB is not available."""
    if database is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Please ensure MongoDB is running on localhost:27017."
        )
    return database
