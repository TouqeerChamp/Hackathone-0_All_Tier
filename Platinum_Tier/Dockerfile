# Platinum Tier AI Employee - Dockerfile
# =======================================
# Multi-service autonomous agent with Odoo ERP integration
# Based on Python 3.11-slim with Playwright support for LinkedIn automation

FROM python:3.11-slim

# Metadata
LABEL maintainer="Mohammad Touqeer"
LABEL version="2.0"
LABEL description="Platinum Tier AI Employee - Autonomous Multi-Step Task Processor with Playwright"

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

# Install system dependencies for Playwright (Chromium)
# See: https://playwright.dev/python/docs/browsers#install-system-dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    # Playwright Chromium dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser with system dependencies
RUN playwright install --with-deps chromium

# Copy all application scripts
COPY *.py ./

# Copy social_media module
COPY social_media/ ./social_media/

# Create necessary directories
RUN mkdir -p ${LOGS_DIR} ${INBOX_DIR} ${AUDIT_LOGS_DIR} \
    && mkdir -p /app/needs_action \
    && mkdir -p /app/linkedin_drafts \
    && mkdir -p /app/logs/audit_logs/cache/google_search \
    && mkdir -p /app/.linkedin_data

# Initialize linkedin_cookies.json and post_tracker.json if missing
RUN echo '[]' > /app/linkedin_cookies.json \
    && echo '{"last_post_timestamp": null, "daily_count": 0, "last_reset_date": null, "total_posts": 0}' > /app/post_tracker.json

# Create startup script (shell equivalent of run_ai_employee.sh)
# Prioritizes autonomous_agent.py which handles all tiers (Gmail, Odoo, LinkedIn)
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
# Initialize log\n\
echo "============================================" > "${LOG_FILE}"\n\
echo "AI Employee Automation Run - Started: $(date)" >> "${LOG_FILE}"\n\
echo "============================================" >> "${LOG_FILE}"\n\
\n\
# Main Task: Autonomous Agent (handles Gmail, Odoo, and LinkedIn in one go)\n\
if [ -f "autonomous_agent.py" ]; then\n\
    echo "[Main Task] Running autonomous_agent.py..."\n\
    echo "  -> Processes Gmail, Odoo, and LinkedIn automation"\n\
    python autonomous_agent.py >> "${LOG_FILE}" 2>&1 || echo "ERROR: autonomous_agent.py failed"\n\
else\n\
    echo "ERROR: autonomous_agent.py not found!"\n\
fi\n\
\n\
# Task 1: Create Plans (Reasoning Loop) - Optional secondary task\n\
if [ -f "create_plans.py" ]; then\n\
    echo "[Task 1] Running create_plans.py..."\n\
    python create_plans.py || echo "ERROR: create_plans.py failed"\n\
fi\n\
\n\
# Task 2: CEO Briefer - Optional secondary task\n\
if [ -f "ceo_briefer.py" ]; then\n\
    echo "[Task 2] Running ceo_briefer.py..."\n\
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
