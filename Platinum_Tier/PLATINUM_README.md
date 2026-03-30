# Platinum Tier AI Employee - Lightweight Cloud-Ready

## Overview

Platinum Tier is a lightweight, cloud-ready version of the AI Employee system that uses Python's built-in process management instead of Docker. This tier is optimized for local development and lightweight deployments.

## Key Features

- ✅ **Environment-Based Configuration**: All credentials stored in `.env` file
- ✅ **Virtual Environment Support**: Isolated Python dependencies via `venv`
- ✅ **Heartbeat Monitoring**: Continuous system health checks every 5 minutes
- ✅ **Gold Tier Logging**: Full audit compliance with JSON Lines logging
- ✅ **Graceful Degradation**: Fault-tolerant service architecture
- ✅ **Lightweight Process Management**: No Docker overhead

## Quick Start

### 1. Prerequisites

- Python 3.8+ installed
- Internet connection (for initial package installation)

### 2. Setup

```batch
# Run the startup script
platinum_start.bat
```

The script will automatically:
1. Create a Python virtual environment (`venv/`)
2. Install all required dependencies
3. Create necessary directories (`logs/`, `inbox/`)
4. Start the Heartbeat Monitor (background)
5. Start the Autonomous Agent (foreground)

### 3. Configure Credentials

Edit the `.env` file with your credentials:

```env
# Odoo ERP
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USER=your_email@gmail.com
ODOO_PASS=your_password

# Google API
GOOGLE_API_KEY=your_api_key
GOOGLE_CSE_ID=your_cse_id

# System Configuration
LOG_LEVEL=INFO
HEARTBEAT_INTERVAL=300
```

## Architecture

### Agent Skills

All functionality is implemented as **Agent Skills** following Gold Tier standards:

| Skill | File | Description |
|-------|------|-------------|
| **Autonomous Agent** | `autonomous_agent.py` | Ralph Wiggum Loop for email processing |
| **CEO Briefer** | `ceo_briefer.py` | Weekly business health briefings |
| **Odoo Client** | `odoo_client.py` | ERP integration via XML-RPC |
| **Gmail Watcher** | `gmail_watcher.py` | Email fetching and processing |
| **Heartbeat** | `heartbeat.py` | System health monitoring |
| **Social Media** | `social_media/social_manager.py` | Social media automation |
| **Graceful Degradation** | `graceful_degradation.py` | Fault tolerance utility |

### Directory Structure

```
Platinum_Tier/
├── .env                      # Environment variables (credentials)
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── credentials.json          # Google OAuth credentials
├── platinum_start.bat        # Startup script
│
├── autonomous_agent.py       # Main email processing agent
├── ceo_briefer.py            # CEO briefing generator
├── heartbeat.py              # System health monitor
├── odoo_client.py            # Odoo ERP client
├── gmail_watcher.py          # Gmail API integration
├── inbox_scanner.py          # Email scanner utility
├── graceful_degradation.py   # Fault tolerance utility
│
├── social_media/             # Social media module
│   ├── social_manager.py     # Social media automation
│   └── post_history.json     # Post history (auto-generated)
│
├── logs/                     # Log directory (auto-generated)
│   └── audit_logs/           # Audit-compliant logs
│       ├── heartbeat.log     # Heartbeat monitoring
│       ├── autonomous_agent_*.log  # Agent actions
│       └── graceful_degradation.log  # Fallback events
│
└── inbox/                    # Email storage (auto-generated)
    └── email_*.json          # Processed emails
```

## Logging Standards

All logs follow **Gold Tier** standards:

### Format

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Audit Logs (JSON Lines)

```json
{"timestamp": "2026-03-30T12:00:00", "event_type": "heartbeat", "status": "success", "service": "Heartbeat_Monitor", "details": {...}}
```

### Log Locations

- **Heartbeat**: `logs/audit_logs/heartbeat.log`
- **Autonomous Agent**: `logs/audit_logs/autonomous_agent_YYYYMMDD.log`
- **Social Media**: `logs/audit_logs/social_media_YYYYMMDD.log`
- **Graceful Degradation**: `logs/audit_logs/graceful_degradation.log`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ODOO_URL` | Odoo server URL | `http://localhost:8069` |
| `ODOO_DB` | Odoo database name | `ai_employee_db` |
| `ODOO_USER` | Odoo username (email) | Required |
| `ODOO_PASS` | Odoo password | Required |
| `GOOGLE_API_KEY` | Google API key | Required |
| `GOOGLE_CSE_ID` | Google Custom Search Engine ID | Required |
| `LOG_LEVEL` | Logging level | `INFO` |
| `HEARTBEAT_INTERVAL` | Heartbeat interval (seconds) | `300` |

### Heartbeat Configuration

The Heartbeat skill logs system health every 5 minutes:

```bash
# Change heartbeat interval in .env
HEARTBEAT_INTERVAL=600  # 10 minutes
```

## Manual Operations

### Start Services Manually

```batch
# Activate virtual environment
venv\Scripts\activate

# Start Heartbeat (background)
start /B python heartbeat.py

# Start Autonomous Agent
python autonomous_agent.py

# Generate CEO Briefing
python ceo_briefer.py
```

### View Logs

```batch
# View latest heartbeat logs
type logs\audit_logs\heartbeat.log

# View today's agent logs
type logs\audit_logs\autonomous_agent_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log
```

### Stop Services

- Press `Ctrl+C` in the terminal to stop the Autonomous Agent
- Heartbeat runs in background - close the terminal window to stop

## Troubleshooting

### Python Not Found

```
[ERROR] Python is not installed or not in PATH
```

**Solution**: Install Python 3.8+ from [python.org](https://www.python.org/downloads/) and check "Add Python to PATH" during installation.

### Credentials Missing

```
[WARNING] .env file not found!
```

**Solution**: Create a `.env` file with your credentials. See the template in the `.env` file.

### Virtual Environment Issues

```
[ERROR] Failed to create virtual environment
```

**Solution**: 
1. Delete the `venv/` folder
2. Run `platinum_start.bat` again

### Import Errors

```
ModuleNotFoundError: No module named 'dotenv'
```

**Solution**: 
```batch
venv\Scripts\activate
pip install -r requirements.txt
```

## Security Best Practices

1. **Never commit `.env`** - Already in `.gitignore`
2. **Protect `credentials.json`** - Contains OAuth secrets
3. **Use strong passwords** - For Odoo and Google accounts
4. **Regular log rotation** - Archive old logs monthly
5. **Monitor heartbeat** - Check `heartbeat.log` for gaps

## Migration from Docker

If you're migrating from a Docker-based setup:

1. Copy your `.env` file from the Docker volume
2. Copy `credentials.json` 
3. Run `platinum_start.bat`
4. Verify logs in `logs/audit_logs/`

## Performance Notes

- **Memory Usage**: ~50-100MB per process
- **CPU Usage**: Minimal (<5% when idle)
- **Disk Usage**: ~10MB for logs per day
- **Startup Time**: ~5-10 seconds

## Support

For issues or questions:
1. Check `logs/audit_logs/` for error details
2. Verify `.env` configuration
3. Ensure Python 3.8+ is installed
4. Review Gold Tier documentation

---

**Platinum Tier** - Lightweight, Cloud-Ready, Production-Grade AI Employee
