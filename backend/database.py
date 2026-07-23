"""
MongoDB Database Configuration
"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", os.getenv("DB_NAME", "deepfake_detector"))

# Global database client
client: Optional[AsyncIOMotorClient] = None
database = None


async def connect_to_mongo():
    """Connect to MongoDB with fallbacks for SSL/TLS"""
    global client, database
    
    kwargs_options = []
    try:
        import certifi
        kwargs_options.append({"tlsCAFile": certifi.where(), "serverSelectionTimeoutMS": 5000})
    except ImportError:
        pass

    kwargs_options.append({"tlsAllowInvalidCertificates": True, "serverSelectionTimeoutMS": 5000})
    kwargs_options.append({"serverSelectionTimeoutMS": 5000})

    for kwargs in kwargs_options:
        temp_client = None
        try:
            temp_client = AsyncIOMotorClient(MONGODB_URL, **kwargs)
            await temp_client.admin.command('ping')
            client = temp_client
            database = client[DATABASE_NAME]
            print(f"[SUCCESS] Connected to MongoDB with options {kwargs}")
            return True
        except Exception as err:
            print(f"[DEBUG] MongoDB connect attempt with {kwargs} failed: {err}")
            if temp_client:
                temp_client.close()

    print(f"[WARNING] Failed to connect to MongoDB at {MONGODB_URL}")
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
