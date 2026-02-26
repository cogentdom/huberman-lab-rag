#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Warning: Redis server is not running. Please start Redis first:"
    echo "redis-server"
    exit 1
fi

# Kill any existing Flask processes on port 8000
echo "Checking for existing Flask processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start the Flask app
echo "Starting Huberman Lab Chat app on http://localhost:8000"
python app/app.py 