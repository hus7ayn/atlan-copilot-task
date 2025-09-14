#!/bin/bash

# ATLAN Customer Copilot - Quick Setup Script
# This script automates the setup process for local development

set -e  # Exit on any error

echo "🚀 ATLAN Customer Copilot - Quick Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the ATLAN_CUSTOMER_COPILOT directory"
    exit 1
fi

print_status "Starting setup process..."

# Step 1: Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION found"
    
    # Check if version is 3.8 or higher
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_success "Python version is compatible (3.8+)"
    else
        print_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Step 2: Check Node.js version
print_status "Checking Node.js version..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    print_success "Node.js $NODE_VERSION found"
    
    # Check if version is 16 or higher
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    if [ "$NODE_MAJOR" -ge 16 ]; then
        print_success "Node.js version is compatible (16+)"
    else
        print_error "Node.js 16 or higher is required. Current version: $NODE_VERSION"
        exit 1
    fi
else
    print_error "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Step 3: Create virtual environment
print_status "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Step 4: Activate virtual environment and install dependencies
print_status "Activating virtual environment and installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Step 5: Set up environment variables
print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env file with your actual API keys"
    else
        print_error "env.example file not found"
        exit 1
    fi
else
    print_warning "Environment file already exists"
fi

# Step 6: Install frontend dependencies
print_status "Installing frontend dependencies..."
cd client
if [ ! -d "node_modules" ]; then
    npm install
    print_success "Frontend dependencies installed"
else
    print_warning "Frontend dependencies already installed"
fi
cd ..

# Step 7: Test backend
print_status "Testing backend setup..."
source venv/bin/activate
python3 -c "
import sys
try:
    from fastapi import FastAPI
    from anthropic import Anthropic
    from tavily import TavilyClient
    print('✅ All backend dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Step 8: Test frontend
print_status "Testing frontend setup..."
cd client
npm list react > /dev/null 2>&1 && print_success "Frontend dependencies verified" || print_error "Frontend setup failed"
cd ..

# Step 9: Final instructions
echo ""
echo "🎉 Setup completed successfully!"
echo "================================"
echo ""
print_status "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - CLAUDE_API_KEY=your_claude_api_key_here"
echo "   - TAVILY_API_KEY=your_tavily_api_key_here"
echo ""
echo "2. Start the backend:"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo ""
echo "3. Start the frontend (in a new terminal):"
echo "   cd client"
echo "   npm start"
echo ""
echo "4. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
print_warning "Don't forget to add your API keys to the .env file!"
echo ""
print_success "Setup complete! Happy coding! 🚀"
