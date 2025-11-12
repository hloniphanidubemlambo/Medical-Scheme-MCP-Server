@echo off
echo ============================================================
echo 🏥 Medical Scheme MCP Server - Windows Startup
echo ============================================================

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    py -m venv .venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Start the server
echo 🚀 Starting Medical Scheme MCP Server...
py run_server.py

pause