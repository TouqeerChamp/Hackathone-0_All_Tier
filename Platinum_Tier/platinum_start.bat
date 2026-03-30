@echo off
REM =============================================================================
REM Platinum Tier AI Employee - Startup Script
REM =============================================================================
REM This script sets up a local Python Virtual Environment (venv),
REM installs requirements, and starts the AI Agent and Heartbeat together.
REM
REM Usage:
REM     platinum_start.bat
REM
REM Processes Started:
REM     1. autonomous_agent.py - Ralph Wiggum Loop (email processing)
REM     2. heartbeat.py - System health monitoring (logs every 5 minutes)
REM
REM Requirements:
REM     - Python 3.8+ installed and in PATH
REM     - Internet connection (for pip install)
REM =============================================================================

echo ============================================================
echo PLATINUM TIER AI EMPLOYEE - STARTUP SCRIPT
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [INFO] Python found: 
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created successfully
) else (
    echo [INFO] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated
echo.

REM Upgrade pip (optional but recommended)
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install requirements
echo [INFO] Installing requirements from requirements.txt...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    pause
    exit /b 1
)
echo [SUCCESS] All requirements installed
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" (
    echo [INFO] Creating logs directory...
    mkdir logs
)
if not exist "logs\audit_logs" (
    mkdir logs\audit_logs
)
if not exist "inbox" (
    echo [INFO] Creating inbox directory...
    mkdir inbox
)
echo [SUCCESS] Directories ready
echo.

REM Verify .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Please create a .env file with your credentials before running.
    echo See .env.example for template.
    pause
    exit /b 1
)
echo [INFO] .env file found - credentials loaded
echo.

echo ============================================================
echo STARTING PLATINUM TIER SERVICES
echo ============================================================
echo.
echo Services to start:
echo   1. autonomous_agent.py - Email processing agent
echo   2. heartbeat.py - System health monitor
echo   3. gmail_watcher.py - Gmail watcher service
echo   4. executive_dashboard.py - Executive Dashboard (separate window)
echo.
echo Logs will be written to:
echo   - logs\audit_logs\autonomous_agent_*.log
echo   - logs\audit_logs\heartbeat.log
echo   - logs\audit_logs\gmail_watcher.log
echo.
echo Press Ctrl+C to stop all services
echo ============================================================
echo.

REM Start Heartbeat in background (silent mode)
echo [STARTING] Heartbeat Monitor...
start /B python heartbeat.py
echo [OK] Heartbeat started in background
timeout /t 2 /nobreak >nul

REM Start Gmail Watcher in background (silent mode)
echo [STARTING] Gmail Watcher...
start /B python gmail_watcher.py
echo [OK] Gmail Watcher started in background
timeout /t 2 /nobreak >nul

REM Start Executive Dashboard in separate window
echo [STARTING] Executive Dashboard...
start "Executive Dashboard" python executive_dashboard.py
echo [OK] Executive Dashboard started in new window
timeout /t 2 /nobreak >nul

REM Start Autonomous Agent in foreground (with output)
echo [STARTING] Autonomous Agent (Ralph Wiggum Loop)...
echo.
python autonomous_agent.py

REM If autonomous_agent.py exits, ask user if they want to restart
echo.
echo ============================================================
echo Autonomous Agent completed
echo ============================================================
echo.
set /p restart="Do you want to run the agent again? (Y/N): "
if /i "%restart%"=="Y" (
    echo Restarting Autonomous Agent...
    goto :eof
) else (
    echo.
    echo [INFO] Stopping all services...
    echo Heartbeat will continue running. Close this window to stop it.
    echo.
    echo ============================================================
    echo PLATINUM TIER STARTUP COMPLETE
    echo ============================================================
    pause
)
