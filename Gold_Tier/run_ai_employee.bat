@echo off
REM ============================================================================
REM AI Employee Automation Runner - Gold Tier
REM ============================================================================
REM This batch file runs all AI automation tasks in sequence:
REM   0. system_health_check.py - System health and Odoo server check
REM   1. inbox_scanner.py - Scan and process existing inbox emails
REM   2. linkedin_automation.py - LinkedIn draft creation
REM   3. create_plans.py - Reasoning loop for task planning
REM
REM Logs are saved to: automation.log
REM Audit logs are saved to: logs/audit_logs/
REM
REM For continuous Gmail monitoring, run watcher.py separately or via
REM Task Scheduler with: start /B python watcher.py
REM ============================================================================

setlocal enabledelayedexpansion

REM Configuration
set "LOG_FILE=%~dp0automation.log"
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "VENV_DIR_ALT=%SCRIPT_DIR%.venv"

REM Initialize log file
echo ============================================================================ > "%LOG_FILE%"
echo AI Employee Automation Run - Started: %DATE% %TIME% >> "%LOG_FILE%"
echo ============================================================================ >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Check for virtual environment
echo [%DATE% %TIME%] Checking for virtual environment... >> "%LOG_FILE%"
echo Checking for virtual environment...

if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [%DATE% %TIME%] Found virtual environment: venv >> "%LOG_FILE%"
    echo Activating virtual environment: venv
    call "%VENV_DIR%\Scripts\activate.bat"
    goto :venv_activated
)

if exist "%VENV_DIR_ALT%\Scripts\activate.bat" (
    echo [%DATE% %TIME%] Found virtual environment: .venv >> "%LOG_FILE%"
    echo Activating virtual environment: .venv
    call "%VENV_DIR_ALT%\Scripts\activate.bat"
    goto :venv_activated
)

echo [%DATE% %TIME%] No virtual environment found. Using system Python. >> "%LOG_FILE%"
echo No virtual environment found. Using system Python.
goto :run_scripts

:venv_activated
echo [%DATE% %TIME%] Virtual environment activated successfully. >> "%LOG_FILE%"

:run_scripts
REM ============================================================================
REM Task 0: Run system_health_check.py (Gold Tier - System Health)
REM ============================================================================
echo. >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo [%DATE% %TIME%] Task 0: system_health_check.py (System Health) >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo.
echo Task 0: system_health_check.py (System Health)

if exist "system_health_check.py" (
    python system_health_check.py >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo [%DATE% %TIME%] WARNING: system_health_check.py reported issues (exit code %ERRORLEVEL%) >> "%LOG_FILE%"
        echo WARNING: system_health_check.py reported issues - continuing with degraded functionality
    ) else (
        echo [%DATE% %TIME%] SUCCESS: system_health_check.py completed successfully >> "%LOG_FILE%"
        echo SUCCESS: system_health_check.py completed
    )
) else (
    echo [%DATE% %TIME%] WARNING: system_health_check.py not found. Skipping... >> "%LOG_FILE%"
    echo WARNING: system_health_check.py not found. Skipping...
)
REM ============================================================================
REM Task 1: Run inbox_scanner.py (Process Existing Inbox Emails)
REM ============================================================================
echo. >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo [%DATE% %TIME%] Task 1: inbox_scanner.py (Email Processing) >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo.
echo Task 1: inbox_scanner.py (Email Processing)

if exist "inbox_scanner.py" (
    python inbox_scanner.py >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo [%DATE% %TIME%] ERROR: inbox_scanner.py failed with exit code %ERRORLEVEL% >> "%LOG_FILE%"
        echo ERROR: inbox_scanner.py failed
    ) else (
        echo [%DATE% %TIME%] SUCCESS: inbox_scanner.py completed successfully >> "%LOG_FILE%"
        echo SUCCESS: inbox_scanner.py completed
    )
) else (
    echo [%DATE% %TIME%] WARNING: inbox_scanner.py not found. Skipping... >> "%LOG_FILE%"
    echo WARNING: inbox_scanner.py not found. Skipping...
)

REM ============================================================================
REM Task 2: Run linkedin_automation.py (LinkedIn Draft Creation)
REM ============================================================================
echo. >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo [%DATE% %TIME%] Task 2: Starting linkedin_automation.py (LinkedIn Drafts) >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo.
echo Task 2: Starting linkedin_automation.py (LinkedIn Drafts)

if exist "linkedin_automation.py" (
    python linkedin_automation.py >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo [%DATE% %TIME%] ERROR: linkedin_automation.py failed with exit code %ERRORLEVEL% >> "%LOG_FILE%"
        echo ERROR: linkedin_automation.py failed
    ) else (
        echo [%DATE% %TIME%] SUCCESS: linkedin_automation.py completed successfully >> "%LOG_FILE%"
        echo SUCCESS: linkedin_automation.py completed
    )
) else (
    echo [%DATE% %TIME%] WARNING: linkedin_automation.py not found. Skipping... >> "%LOG_FILE%"
    echo WARNING: linkedin_automation.py not found. Skipping...
)

REM ============================================================================
REM Task 3: Run create_plans.py (Reasoning Loop)
REM NOTE: This script processes emails in needs_action folder.
REM       Google Search API calls may take time.
REM ============================================================================
echo. >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo [%DATE% %TIME%] Task 3: Starting create_plans.py (Reasoning Loop) >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo.
echo Task 3: Starting create_plans.py (Reasoning Loop)

if exist "create_plans.py" (
    python create_plans.py
    if errorlevel 1 (
        echo [%DATE% %TIME%] create_plans.py completed with exit code %ERRORLEVEL% >> "%LOG_FILE%"
        echo create_plans.py completed with exit code %ERRORLEVEL%
    ) else (
        echo [%DATE% %TIME%] SUCCESS: create_plans.py completed successfully >> "%LOG_FILE%"
        echo SUCCESS: create_plans.py completed
    )
) else (
    echo [%DATE% %TIME%] WARNING: create_plans.py not found. Skipping... >> "%LOG_FILE%"
    echo WARNING: create_plans.py not found. Skipping...
)

REM ============================================================================
REM Task 4: Run ceo_briefer.py (CEO Weekly Briefing - Gold Tier Phase 3)
REM NOTE: This generates the CEO briefing with business health, marketing pulse,
REM       and system integrity reports.
REM ============================================================================
echo. >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo [%DATE% %TIME%] Task 4: Starting ceo_briefer.py (CEO Weekly Briefing) >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo.
echo Task 4: Starting ceo_briefer.py (CEO Weekly Briefing)

if exist "ceo_briefer.py" (
    python ceo_briefer.py >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo [%DATE% %TIME%] WARNING: ceo_briefer.py completed with exit code %ERRORLEVEL% >> "%LOG_FILE%"
        echo WARNING: ceo_briefer.py completed with exit code %ERRORLEVEL%
    ) else (
        echo [%DATE% %TIME%] SUCCESS: ceo_briefer.py completed successfully >> "%LOG_FILE%"
        echo SUCCESS: ceo_briefer.py completed - CEO Briefing generated
    )
) else (
    echo [%DATE% %TIME%] WARNING: ceo_briefer.py not found. Skipping... >> "%LOG_FILE%"
    echo WARNING: ceo_briefer.py not found. Skipping...
)

REM ============================================================================
REM Cleanup and Exit
REM ============================================================================
echo. >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo [%DATE% %TIME%] All tasks completed! >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo [%DATE% %TIME%] AI Employee Automation Run - Finished >> "%LOG_FILE%"
echo [%DATE% %TIME%] Log file: %LOG_FILE% >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo.
echo ==========================================
echo All tasks completed!
echo ==========================================
echo.
echo Log file: %LOG_FILE%

REM Deactivate virtual environment if it was activated
if defined VIRTUAL_ENV (
    deactivate
)

endlocal
exit /b 0
