#!/bin/bash
# ============================================================================
# AI Employee Automation Runner - Platinum Tier (Shell Equivalent)
# ============================================================================
# This script runs all AI automation tasks in sequence:
#   0. system_health_check.py - System health and Odoo server check
#   1. inbox_scanner.py - Scan and process existing inbox emails
#   2. linkedin_automation.py - LinkedIn draft creation
#   3. create_plans.py - Reasoning loop for task planning
#   4. ceo_briefer.py - CEO Weekly Briefing
#
# Usage:
#   ./run_ai_employee.sh
#
# Logs are saved to: automation.log
# Audit logs are saved to: logs/audit_logs/
# ============================================================================

set -e

# Configuration
LOG_FILE="$(pwd)/automation.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to script directory
cd "${SCRIPT_DIR}"

# Initialize log file
echo "============================================================================" > "${LOG_FILE}"
echo "AI Employee Automation Run - Started: $(date)" >> "${LOG_FILE}"
echo "============================================================================" >> "${LOG_FILE}"
echo "" >> "${LOG_FILE}"

echo "============================================================================"
echo "AI Employee Automation Runner - Platinum Tier"
echo "Started: $(date)"
echo "============================================================================"

# Function to run a Python script with error handling
run_script() {
    local script_name="$1"
    local task_name="$2"
    
    echo ""
    echo "[Task] ${task_name}"
    echo "============================================================================" >> "${LOG_FILE}"
    echo "[$(date)] Task: ${task_name}" >> "${LOG_FILE}"
    echo "============================================================================" >> "${LOG_FILE}"
    
    if [ -f "${script_name}" ]; then
        if python "${script_name}" >> "${LOG_FILE}" 2>&1; then
            echo "✓ SUCCESS: ${script_name} completed"
            echo "[$(date)] SUCCESS: ${script_name} completed successfully" >> "${LOG_FILE}"
        else
            local exit_code=$?
            echo "⚠ WARNING: ${script_name} completed with exit code ${exit_code}"
            echo "[$(date)] WARNING: ${script_name} completed with exit code ${exit_code}" >> "${LOG_FILE}"
        fi
    else
        echo "⚠ WARNING: ${script_name} not found. Skipping..."
        echo "[$(date)] WARNING: ${script_name} not found. Skipping..." >> "${LOG_FILE}"
    fi
}

# Task 0: System Health Check (if exists)
run_script "system_health_check.py" "System Health Check"

# Task 1: Inbox Scanner
run_script "inbox_scanner.py" "Inbox Scanner (Email Processing)"

# Task 2: LinkedIn Automation
run_script "linkedin_automation.py" "LinkedIn Draft Creation"

# Task 3: Create Plans (Reasoning Loop)
echo ""
echo "[Task] Create Plans (Reasoning Loop)"
echo "NOTE: Google Search API calls may take time..."
run_script "create_plans.py" "Create Plans (Reasoning Loop)"

# Task 4: CEO Briefer
run_script "ceo_briefer.py" "CEO Weekly Briefing"

# Cleanup and Exit
echo ""
echo "============================================================================"
echo "All tasks completed: $(date)"
echo "============================================================================"
echo "Log file: ${LOG_FILE}"
echo ""

echo "============================================================================" >> "${LOG_FILE}"
echo "[$(date)] All tasks completed!" >> "${LOG_FILE}"
echo "[$(date)] AI Employee Automation Run - Finished" >> "${LOG_FILE}"
echo "============================================================================" >> "${LOG_FILE}"

exit 0
