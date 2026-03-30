# Platinum Tier AI Employee - Dockerfile
# =======================================
# Multi-service autonomous agent with Odoo ERP integration
# Based on Python 3.11-slim

FROM python:3.11-slim

# Metadata
LABEL maintainer="Mohammad Touqeer"
LABEL version="1.0"
LABEL description="Platinum Tier AI Employee - Autonomous Multi-Step Task Processor"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Application settings
    APP_HOME=/app \
    LOGS_DIR=/app/logs \
    INBOX_DIR=/app/inbox \
    AUDIT_LOGS_DIR=/app/logs/audit_logs

# Set working directory
WORKDIR ${APP_HOME}

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application scripts
COPY *.py ./
COPY .env .
COPY credentials.json ./

# Copy social_media module
COPY social_media/ ./social_media/

# Create necessary directories
RUN mkdir -p ${LOGS_DIR} ${INBOX_DIR} ${AUDIT_LOGS_DIR} \
    && mkdir -p /app/needs_action \
    && mkdir -p /app/linkedin_drafts \
    && mkdir -p /app/logs/audit_logs/cache/google_search

# Create startup script (shell equivalent of run_ai_employee.bat)
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "============================================"\n\
echo "AI Employee Automation Runner - Platinum Tier"\n\
echo "Started: $(date)"\n\
echo "============================================"\n\
\n\
# Log file\n\
LOG_FILE="/app/automation.log"\n\
\n\
# Initialize log\
echo "============================================" > "${LOG_FILE}"\n\
echo "AI Employee Automation Run - Started: $(date)" >> "${LOG_FILE}"\n\
echo "============================================" >> "${LOG_FILE}"\n\
\n\
# Task 0: System Health Check (if exists)\n\
if [ -f "system_health_check.py" ]; then\n\
    echo "[Task 0] Running system_health_check.py..."\n\
    python system_health_check.py >> "${LOG_FILE}" 2>&1 || echo "WARNING: system_health_check.py reported issues"\n\
fi\n\
\n\
# Task 1: Inbox Scanner\n\
if [ -f "inbox_scanner.py" ]; then\n\
    echo "[Task 1] Running inbox_scanner.py..."\n\
    python inbox_scanner.py >> "${LOG_FILE}" 2>&1 || echo "ERROR: inbox_scanner.py failed"\n\
fi\n\
\n\
# Task 2: LinkedIn Automation\n\
if [ -f "linkedin_automation.py" ]; then\n\
    echo "[Task 2] Running linkedin_automation.py..."\n\
    python linkedin_automation.py >> "${LOG_FILE}" 2>&1 || echo "ERROR: linkedin_automation.py failed"\n\
fi\n\
\n\
# Task 3: Create Plans (Reasoning Loop)\n\
if [ -f "create_plans.py" ]; then\n\
    echo "[Task 3] Running create_plans.py..."\n\
    python create_plans.py || echo "ERROR: create_plans.py failed"\n\
fi\n\
\n\
# Task 4: CEO Briefer\n\
if [ -f "ceo_briefer.py" ]; then\n\
    echo "[Task 4] Running ceo_briefer.py..."\n\
    python ceo_briefer.py >> "${LOG_FILE}" 2>&1 || echo "WARNING: ceo_briefer.py reported issues"\n\
fi\n\
\n\
echo "============================================"\n\
echo "All tasks completed: $(date)"\n\
echo "============================================"\n\
echo "Log file: ${LOG_FILE}"\n\
' > /app/run_ai_employee.sh \
    && chmod +x /app/run_ai_employee.sh

# Create entrypoint script for continuous operation
RUN echo '#!/bin/bash\n\
\n\
# Entrypoint script for Always-On operation\n\
# This script ensures the container restarts if it crashes\n\
\n\
echo "============================================"\n\
echo "AI Employee Container Starting..."\n\
echo "============================================"\n\
echo "Hostname: $(hostname)"\n\
echo "Working Directory: $(pwd)"\n\
echo "============================================"\n\
\n\
# Wait for Odoo DB to be ready (if using docker-compose)\n\
if [ -n "${ODOO_DB_HOST}" ]; then\n\
    echo "Waiting for Odoo database at ${ODOO_DB_HOST}..."\n\
    while ! nc -z ${ODOO_DB_HOST} 5432 2>/dev/null; do\n\
        sleep 2\n\
    done\n\
    echo "✓ Database is ready!"\n\
fi\n\
\n\
# Run the main automation script\n\
exec /app/run_ai_employee.sh\n\
' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Expose ports (for monitoring/debugging if needed)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command (can be overridden)
CMD []
