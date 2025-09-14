#!/bin/bash

# Debug: Show all environment variables
echo "🔍 Environment variables:"
env | grep -i port || echo "No PORT variable found"

# Get port from environment variable or use default
PORT=${PORT:-8000}

echo "🚀 Starting server on port $PORT"
echo "🔧 PORT variable value: $PORT"

# Start uvicorn with the determined port
uvicorn main:app --host 0.0.0.0 --port $PORT
