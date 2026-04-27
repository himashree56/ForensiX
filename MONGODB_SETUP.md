# MongoDB Setup Guide

## Option 1: Using Docker (Recommended)

### Prerequisites
- Install Docker Desktop for Windows from https://www.docker.com/products/docker-desktop/

### Start MongoDB with Docker
```bash
docker run -d --name deepfake-mongodb -p 27017:27017 -e MONGO_INITDB_DATABASE=deepfake_detector mongo:7.0
```

### Stop MongoDB
```bash
docker stop deepfake-mongodb
```

### Remove MongoDB Container
```bash
docker rm deepfake-mongodb
```

## Option 2: Using Docker Compose

From the project root directory:

```bash
docker-compose up mongodb -d
```

This will start MongoDB as defined in `docker-compose.yml`.

## Option 3: Install MongoDB Locally

### Download and Install
1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Install MongoDB following the installer instructions
3. MongoDB will run on `localhost:27017` by default

### Start MongoDB Service (Windows)
```bash
net start MongoDB
```

### Stop MongoDB Service (Windows)
```bash
net stop MongoDB
```

## Verify MongoDB is Running

### Using MongoDB Shell (mongosh)
```bash
mongosh
```

You should see a connection message if MongoDB is running.

### Using Python
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['deepfake_detector']
print("Connected to MongoDB!")
```

## Environment Variables

The backend uses these environment variables for MongoDB connection:

- `MONGODB_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `DATABASE_NAME`: Database name (default: `deepfake_detector`)

You can set these in a `.env` file in the `backend` directory:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=deepfake_detector
```

## Testing the Connection

Once MongoDB is running, start the backend:

```bash
cd backend
.\\venv\\Scripts\\activate
python main.py
```

You should see:
```
Connected to MongoDB at mongodb://localhost:27017
```

## Troubleshooting

### Connection Refused
- Make sure MongoDB is running
- Check if port 27017 is available
- Verify firewall settings

### Authentication Failed
- If using authentication, update `MONGODB_URL` with credentials:
  ```
  mongodb://username:password@localhost:27017
  ```

### Database Not Created
- MongoDB creates databases automatically when you first insert data
- Upload and analyze a video to create the database

## Viewing Data

### Using MongoDB Compass (GUI)
1. Download from: https://www.mongodb.com/try/download/compass
2. Connect to `mongodb://localhost:27017`
3. Browse the `deepfake_detector` database
4. View the `analyses` collection

### Using mongosh (CLI)
```bash
mongosh
use deepfake_detector
db.analyses.find().pretty()
```

## Note

The application will work without MongoDB, but history features will be disabled. Analysis results will still be returned but not saved.
