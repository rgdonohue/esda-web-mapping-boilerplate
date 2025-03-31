#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn is not installed"
    echo "Installing uvicorn..."
    pip install uvicorn
fi

# Set default port if not specified
PORT=${BACKEND_PORT:-8000}

# Start the FastAPI server
echo "Starting backend server on port $PORT..."
uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT 