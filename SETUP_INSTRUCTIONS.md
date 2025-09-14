# 🚀 Complete Setup Instructions
## ATLAN Customer Copilot - Local Development Environment

This guide provides step-by-step instructions to set up and run the ATLAN Customer Copilot project locally on your machine.

## 📋 Prerequisites

### System Requirements
- **Operating System**: macOS, Windows, or Linux
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **npm**: 8.0 or higher (comes with Node.js)
- **Git**: For cloning the repository

### API Keys Required
- **Anthropic Claude API Key**: For AI processing
- **Tavily API Key**: For real-time web search

## 🔧 Step-by-Step Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd ATLAN_CUSTOMER_COPILOT

# Verify you're in the correct directory
ls -la
# You should see: main.py, requirements.txt, client/, ai_pipeline/, etc.
```

### Step 2: Set Up Python Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
which python
# Should show: /path/to/ATLAN_CUSTOMER_COPILOT/venv/bin/python
```

### Step 3: Install Python Dependencies

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
# You should see: fastapi, uvicorn, anthropic, tavily-python, etc.
```

### Step 4: Set Up Environment Variables

```bash
# Copy the environment template
cp env.example .env

# Edit the .env file with your API keys
nano .env
# or use your preferred editor: vim, code, etc.
```

**Edit the `.env` file with your actual API keys:**

```env
# Claude API Configuration
CLAUDE_API_KEY=your_actual_claude_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_TEMPERATURE=0.1
CLAUDE_MAX_TOKENS=1000

# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True

# CORS Configuration
CLIENT_URL=http://localhost:3000

# Tavily API Configuration
TAVILY_API_KEY=your_actual_tavily_api_key_here
TAVILY_TIMEOUT=30
TAVILY_MAX_RESULTS=5
```

### Step 5: Set Up Frontend (React)

```bash
# Navigate to client directory
cd client

# Install Node.js dependencies
npm install

# Verify installation
npm list
# You should see: react, typescript, axios, etc.

# Go back to project root
cd ..
```

### Step 6: Test the Backend

```bash
# Make sure you're in project root and virtual environment is activated
source venv/bin/activate

# Test the backend server
python3 main.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
🚀 Initializing Simple Tavily System...
✅ Claude API client initialized successfully
✅ Sentiment Agent initialized
✅ Tavily RAG Integration initialized
✅ Simple Tavily System initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**If you see errors:**
- Check that your API keys are correct in `.env`
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Make sure virtual environment is activated

### Step 7: Test the Frontend

```bash
# In a new terminal window/tab
cd client

# Start the React development server
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view client in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.
```

### Step 8: Verify Everything is Working

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/api/health
   # Should return: {"status":"healthy","timestamp":"..."}
   ```

2. **Frontend Access:**
   - Open http://localhost:3000 in your browser
   - You should see the ATLAN Customer Copilot interface

3. **Test File Upload:**
   ```bash
   # Test file upload functionality
   echo "This is a test ticket about connecting to Snowflake." > test.txt
   curl -X POST -F "file=@test.txt" http://localhost:8000/api/upload
   # Should return JSON with processed ticket data
   rm test.txt
   ```

## 🎯 Quick Start Commands

### Start Everything (Recommended)

```bash
# Terminal 1: Start Backend
cd ATLAN_CUSTOMER_COPILOT
source venv/bin/activate
python3 main.py

# Terminal 2: Start Frontend
cd ATLAN_CUSTOMER_COPILOT/client
npm start
```

### Alternative: Use the Startup Script

```bash
# From project root
python3 start_full_system.py
# This will start both backend and frontend automatically
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. **"ModuleNotFoundError: No module named 'fastapi'"**
```bash
# Solution: Virtual environment not activated
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. **"Address already in use" (Port 8000)**
```bash
# Solution: Kill existing process
pkill -f "python.*main.py"
# Or use different port
uvicorn main:app --port 8001
```

#### 3. **"npm: command not found"**
```bash
# Solution: Install Node.js
# Visit: https://nodejs.org/
# Download and install LTS version
```

#### 4. **"Claude API error" or "Tavily API error"**
```bash
# Solution: Check API keys
cat .env
# Verify keys are correct and have no extra spaces
```

#### 5. **Frontend shows "Error connecting to server"**
```bash
# Solution: Check backend is running
curl http://localhost:8000/api/health
# If backend is down, restart it
```

#### 6. **"Permission denied" on macOS/Linux**
```bash
# Solution: Fix permissions
chmod +x venv/bin/activate
chmod +x client/node_modules/.bin/*
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=True
python3 main.py

# Check logs for detailed error information
tail -f logs/app.log  # if logging is configured
```

## 📊 Verify Installation

### Backend Tests

```bash
# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/supported-formats
curl http://localhost:8000/api/tickets
curl http://localhost:8000/api/stats
```

### Frontend Tests

```bash
cd client
npm test
# Run all tests
npm run test -- --coverage
# Run with coverage report
```

### Integration Test

```bash
# Test the complete pipeline
curl -X POST http://localhost:8000/api/interactive-agent \
  -H "Content-Type: application/json" \
  -d '{"text": "How do I connect to Snowflake?"}'
```

## 🚀 Production Deployment

### Build for Production

```bash
# Build frontend
cd client
npm run build

# The build files will be in client/build/
```

### Environment Variables for Production

```env
# Production environment
DEBUG=False
CLAUDE_API_KEY=your_production_claude_key
TAVILY_API_KEY=your_production_tavily_key
PORT=8000
HOST=0.0.0.0
```

## 📁 Project Structure

```
ATLAN_CUSTOMER_COPILOT/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── env.example           # Environment template
├── ai_pipeline/          # AI processing modules
│   ├── sentiment_agent.py
│   ├── simple_tavily_system.py
│   ├── tavily_rag_integration.py
│   └── file_parser.py
├── client/               # React frontend
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   └── pages/
│   └── public/
└── README.md
```

## 🔧 Development Tools

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

### Useful Commands

```bash
# Check Python version
python3 --version

# Check Node.js version
node --version

# Check npm version
npm --version

# List installed Python packages
pip list

# List installed Node packages
npm list

# Check if ports are in use
lsof -i :8000  # Backend port
lsof -i :3000  # Frontend port
```

## 🆘 Getting Help

### If You're Still Stuck

1. **Check the logs:**
   ```bash
   # Backend logs
   python3 main.py 2>&1 | tee backend.log
   
   # Frontend logs
   cd client && npm start 2>&1 | tee frontend.log
   ```

2. **Verify all services:**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/api/health
   
   # Check if frontend is running
   curl http://localhost:3000
   ```

3. **Reset everything:**
   ```bash
   # Clean install
   rm -rf venv node_modules client/node_modules
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd client && npm install
   ```

4. **Check system requirements:**
   ```bash
   # Python version
   python3 --version  # Should be 3.8+
   
   # Node.js version
   node --version     # Should be 16+
   
   # Available memory
   free -h            # Linux
   vm_stat            # macOS
   ```

### Support Resources

- **Documentation**: Check README.md and other .md files
- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **GitHub Issues**: Create an issue with detailed error logs
- **Community**: Check project discussions

---

## ✅ Success Checklist

- [ ] Repository cloned successfully
- [ ] Python virtual environment created and activated
- [ ] All Python dependencies installed
- [ ] Environment variables configured with API keys
- [ ] Backend server starts without errors
- [ ] Frontend development server starts without errors
- [ ] Health check endpoint returns success
- [ ] Frontend loads in browser
- [ ] File upload functionality works
- [ ] Interactive agent responds to queries

**🎉 Congratulations! Your ATLAN Customer Copilot is now running locally!**

You can now:
- Upload files for processing
- Use the interactive agent
- View ticket analytics
- Test the complete AI pipeline

For any issues, refer to the troubleshooting section above or check the project documentation.
