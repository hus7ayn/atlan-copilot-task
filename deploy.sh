#!/bin/bash

# Atlan Customer Copilot Deployment Script
echo "🚀 Starting deployment process..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway whoami || railway login

# Initialize Railway project (if not already initialized)
if [ ! -f "railway.json" ]; then
    echo "🚂 Initializing Railway project..."
    railway init
fi

# Set environment variables
echo "🔧 Setting up environment variables..."
echo "Please set your API keys in Railway dashboard:"
echo "1. Go to your Railway project dashboard"
echo "2. Go to Variables tab"
echo "3. Add the following variables:"
echo "   - CLAUDE_API_KEY=your_claude_api_key"
echo "   - TAVILY_API_KEY=your_tavily_api_key"
echo "   - DEBUG=False"
echo "   - HOST=0.0.0.0"

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at: https://your-app-name.railway.app"
echo "📊 Monitor your deployment at: https://railway.app/dashboard"
