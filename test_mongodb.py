"""
Quick MongoDB Connection Test
Run this to verify MongoDB is accessible
"""
from pymongo import MongoClient
from datetime import datetime

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        # Try to connect to MongoDB
        print("Attempting to connect to MongoDB...")
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB!")
        
        # Get database
        db = client['deepfake_detector']
        print(f"✓ Database 'deepfake_detector' is accessible")
        
        # Try to insert a test document
        test_collection = db['test']
        test_doc = {
            'test': True,
            'timestamp': datetime.utcnow(),
            'message': 'MongoDB connection test'
        }
        result = test_collection.insert_one(test_doc)
        print(f"✓ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({'_id': result.inserted_id})
        print("✓ Test document cleaned up")
        
        # List databases
        print("\nAvailable databases:")
        for db_name in client.list_database_names():
            print(f"  - {db_name}")
        
        # Close connection
        client.close()
        print("\n✓ MongoDB is ready to use!")
        return True
        
    except Exception as e:
        print(f"\n✗ MongoDB connection failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if MongoDB is running:")
        print("   - Windows: Open Services and look for 'MongoDB Server'")
        print("   - Or run: mongosh")
        print("\n2. Verify MongoDB is listening on port 27017")
        print("\n3. If using MongoDB Compass, try connecting to:")
        print("   mongodb://localhost:27017")
        return False

if __name__ == "__main__":
    test_mongodb_connection()
