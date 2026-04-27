# 🔧 How to Start MongoDB on Your Machine

## Quick Start Guide

Since you already have MongoDB installed, you just need to start the service. Here are the methods:

---

## Method 1: Start MongoDB Service (Recommended)

### Using PowerShell (Run as Administrator)
1. **Right-click PowerShell** → Select "Run as Administrator"
2. Run this command:
   ```powershell
   net start MongoDB
   ```

### Using Services GUI
1. Press `Win + R`
2. Type `services.msc` and press Enter
3. Find "MongoDB Server" in the list
4. Right-click → Select "Start"
5. (Optional) Right-click → Properties → Set "Startup type" to "Automatic"

---

## Method 2: Start MongoDB Manually

If the service doesn't exist, start MongoDB manually:

```powershell
# Navigate to MongoDB bin directory (adjust path if different)
cd "C:\Program Files\MongoDB\Server\7.0\bin"

# Start MongoDB
.\mongod.exe --dbpath "C:\data\db"
```

**Note:** You may need to create the data directory first:
```powershell
mkdir C:\data\db
```

---

## Method 3: Check if MongoDB is Already Running

Open a new terminal and run:
```bash
mongosh
```

If you see a MongoDB shell prompt, it's already running!

---

## Verify MongoDB is Running

After starting MongoDB, test the connection:

```bash
# From the project root
python test_mongodb.py
```

You should see:
```
✓ Successfully connected to MongoDB!
✓ Database 'deepfake_detector' is accessible
✓ Test document inserted with ID: ...
✓ Test document cleaned up
✓ MongoDB is ready to use!
```

---

## Common MongoDB Locations

### Default Installation Paths:
- **Program Files**: `C:\Program Files\MongoDB\Server\7.0\bin\`
- **Data Directory**: `C:\data\db\`
- **Config File**: `C:\Program Files\MongoDB\Server\7.0\bin\mongod.cfg`

### Default Connection:
- **URL**: `mongodb://localhost:27017`
- **Port**: `27017`

---

## Troubleshooting

### "Service name 'MongoDB' not found"
The service might have a different name. Check with:
```powershell
Get-Service | Where-Object {$_.DisplayName -like "*mongo*"}
```

Common service names:
- `MongoDB`
- `MongoDB Server`
- `MongoDB Server (MongoDB)`

### "Access is denied"
You need administrator privileges:
1. Right-click PowerShell
2. Select "Run as Administrator"
3. Try the command again

### "mongod.exe not found"
MongoDB might be installed in a different location. Search for it:
```powershell
Get-ChildItem -Path "C:\Program Files" -Filter "mongod.exe" -Recurse -ErrorAction SilentlyContinue
```

### Port 27017 Already in Use
Check what's using the port:
```powershell
netstat -ano | findstr :27017
```

---

## After Starting MongoDB

Once MongoDB is running:

1. **Test the connection**:
   ```bash
   python test_mongodb.py
   ```

2. **Start the backend** (it will auto-connect):
   ```bash
   cd backend
   .\\venv\\Scripts\\activate
   python main.py
   ```

   You should see:
   ```
   ✓ Connected to MongoDB at mongodb://localhost:27017
   ```

3. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

4. **Use the app** with full history features! 🎉

---

## MongoDB Compass (Optional GUI)

If you want a visual interface for MongoDB:

1. **Download**: https://www.mongodb.com/try/download/compass
2. **Install** MongoDB Compass
3. **Connect** to: `mongodb://localhost:27017`
4. **Browse** the `deepfake_detector` database

---

## Quick Commands Reference

```powershell
# Start MongoDB service (as admin)
net start MongoDB

# Stop MongoDB service (as admin)
net stop MongoDB

# Check MongoDB status
Get-Service MongoDB

# Connect to MongoDB shell
mongosh

# Test Python connection
python test_mongodb.py
```

---

## What Happens Without MongoDB?

Don't worry! The app still works:
- ✅ Video analysis works normally
- ✅ Results displayed immediately
- ⚠️ History features disabled
- ⚠️ Data not saved between sessions

---

## Need Help?

If you're still having trouble:
1. Check if MongoDB is installed: `mongod --version`
2. Look for MongoDB in Services: `services.msc`
3. Try connecting with mongosh: `mongosh`
4. Check the error message in `test_mongodb.py`

The backend will show you exactly what's wrong when it tries to connect!
