@echo off
REM ATLAN Customer Copilot - Quick Setup Script for Windows
REM This script automates the setup process for local development

echo 🚀 ATLAN Customer Copilot - Quick Setup
echo ========================================

REM Check if we're in the right directory
if not exist "main.py" (
    echo [ERROR] Please run this script from the ATLAN_CUSTOMER_COPILOT directory
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found. Please run from the correct directory.
    pause
    exit /b 1
)

echo [INFO] Starting setup process...

REM Step 1: Check Python version
echo [INFO] Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% found

REM Step 2: Check Node.js version
echo [INFO] Checking Node.js version...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 16 or higher.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo [SUCCESS] Node.js %NODE_VERSION% found

REM Step 3: Create virtual environment
echo [INFO] Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)

REM Step 4: Activate virtual environment and install dependencies
echo [INFO] Activating virtual environment and installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [SUCCESS] Python dependencies installed

REM Step 5: Set up environment variables
echo [INFO] Setting up environment variables...
if not exist ".env" (
    if exist "env.example" (
        copy env.example .env >nul
        echo [SUCCESS] Environment file created from template
        echo [WARNING] Please edit .env file with your actual API keys
    ) else (
        echo [ERROR] env.example file not found
        pause
        exit /b 1
    )
) else (
    echo [WARNING] Environment file already exists
)

REM Step 6: Install frontend dependencies
echo [INFO] Installing frontend dependencies...
cd client
if not exist "node_modules" (
    npm install
    echo [SUCCESS] Frontend dependencies installed
) else (
    echo [WARNING] Frontend dependencies already installed
)
cd ..

REM Step 7: Test backend
echo [INFO] Testing backend setup...
call venv\Scripts\activate.bat
python -c "import fastapi, anthropic, tavily; print('✅ All backend dependencies imported successfully')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Backend dependencies test failed
    pause
    exit /b 1
)

REM Step 8: Test frontend
echo [INFO] Testing frontend setup...
cd client
npm list react >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Frontend setup failed
    pause
    exit /b 1
)
echo [SUCCESS] Frontend dependencies verified
cd ..

REM Step 9: Final instructions
echo.
echo 🎉 Setup completed successfully!
echo ================================
echo.
echo [INFO] Next steps:
echo 1. Edit .env file with your API keys:
echo    - CLAUDE_API_KEY=your_claude_api_key_here
echo    - TAVILY_API_KEY=your_tavily_api_key_here
echo.
echo 2. Start the backend:
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
echo 3. Start the frontend (in a new command prompt):
echo    cd client
echo    npm start
echo.
echo 4. Access the application:
echo    - Frontend: http://localhost:3000
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo [WARNING] Don't forget to add your API keys to the .env file!
echo.
echo [SUCCESS] Setup complete! Happy coding! 🚀
pause
