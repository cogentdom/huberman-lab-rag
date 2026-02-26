# Huberman Lab Chat - Quick Start Guide

## Prerequisites
1. **Redis**: Make sure Redis server is running
   ```bash
   redis-server
   ```

2. **Virtual Environment**: The `.venv` directory should exist with all dependencies installed

## Running the App

### Option 1: Use the startup script (Recommended)
```bash
./run_app.sh
```

### Option 2: Manual startup
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the app
python app/app.py
```

## Access the App
- **Web Interface**: http://localhost:8000
- **API Endpoint**: http://localhost:8000/query (POST)

## Troubleshooting

### Port 5000 in use (AirPlay Receiver)
The app now uses port 8000 to avoid conflicts with macOS AirPlay Receiver.

### "No module named 'flask'" error
Make sure you're running from the project root directory and the virtual environment is activated:
```bash
cd /path/to/huberman-lab-rag
source .venv/bin/activate
python app/app.py
```

### Redis connection errors
Ensure Redis is running:
```bash
# Start Redis
redis-server

# Test Redis connection
redis-cli ping
```

## API Usage Example
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the benefits of cold exposure?"}'
```

## Stopping the App
- Press `Ctrl+C` in the terminal where the app is running
- Or kill the process: `lsof -ti:8000 | xargs kill -9` 