#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if we're in the frontend directory
if [ ! -d "frontend" ]; then
    echo "Error: frontend directory not found"
    echo "Please run this script from the project root"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Set default port if not specified
PORT=${FRONTEND_PORT:-3000}

# Start the development server
echo "Starting frontend development server on port $PORT..."
npm run dev -- --port $PORT 