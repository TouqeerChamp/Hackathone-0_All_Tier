#!/usr/bin/env python3
"""
Executive Dashboard Skill - Platinum Phase 3
=============================================
Real-time executive status display that shows LIVE STATUS summary.

Reads the latest CEO_Weekly_Briefing.md and heartbeat.log to display
a live status summary on the terminal every 10 minutes.

Usage:
    python executive_dashboard.py

Or run in background:
    start /B python executive_dashboard.py

Configuration:
    DASHBOARD_INTERVAL - Interval in seconds (default: 600 = 10 minutes)
"""

import os
import sys
import time
import json
import logging
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DASHBOARD_INTERVAL = int(os.getenv("DASHBOARD_INTERVAL", "600"))  # Default: 10 minutes
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Paths
LOGS_DIR = Path("logs/audit_logs")
HEARTBEAT_LOG = LOGS_DIR / "heartbeat.log"
BRIEFING_FILE = Path("CEO_Weekly_Briefing.md")
AUDIT_LOG_FILE = LOGS_DIR / "executive_dashboard.log"

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logger
dashboard_logger = logging.getLogger("ExecutiveDashboard")
dashboard_logger.setLevel(getattr(logging, LOG_LEVEL))

# File handler
file_handler = logging.FileHandler(AUDIT_LOG_FILE, encoding='utf-8')
file_handler.setLevel(getattr(logging, LOG_LEVEL))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL))

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

dashboard_logger.addHandler(file_handler)
dashboard_logger.addHandler(console_handler)

# Graceful shutdown flag
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    shutdown_requested = True
    dashboard_logger.info(f"Received signal {signum}, initiating graceful shutdown...")


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def read_latest_briefing() -> Optional[Dict[str, Any]]:
    """
    Read and parse the latest CEO_Weekly_Briefing.md file.
    
    Returns:
        Dictionary containing briefing summary or None if not found
    """
    if not BRIEFING_FILE.exists():
        return None
    
    try:
        with open(BRIEFING_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key information from the briefing
        briefing_data = {
            "file": str(BRIEFING_FILE),
            "last_modified": datetime.fromtimestamp(
                BRIEFING_FILE.stat().st_mtime
            ).isoformat(),
            "size_bytes": BRIEFING_FILE.stat().st_size,
            "health_status": "Unknown",
            "degradation_count": 0,
            "emails_processed": 0,
            "tasks_completed": 0
        }
        
        # Parse health status
        if "**Overall Health Status:**" in content:
            for line in content.split('\n'):
                if "**Overall Health Status:**" in line:
                    if "CRITICAL" in line:
                        briefing_data["health_status"] = "CRITICAL"
                    elif "DEGRADED" in line:
                        briefing_data["health_status"] = "DEGRADED"
                    elif "HEALTHY" in line or "Healthy" in line:
                        briefing_data["health_status"] = "HEALTHY"
                    break
        
        # Parse degradation count
        if "service failures detected" in content:
            for line in content.split('\n'):
                if "service failures detected" in line:
                    try:
                        # Extract number from text like "Critical system health: 4 service failures detected"
                        parts = line.split(':')
                        if len(parts) > 1:
                            num_str = parts[1].strip().split()[0]
                            briefing_data["degradation_count"] = int(num_str)
                    except (ValueError, IndexError):
                        pass
                    break
        
        # Parse emails processed
        if "Emails Processed:" in content:
            for line in content.split('\n'):
                if "Emails Processed:" in line:
                    try:
                        num_str = line.split(':')[1].strip()
                        briefing_data["emails_processed"] = int(num_str)
                    except (ValueError, IndexError):
                        pass
                    break
        
        # Parse tasks completed
        if "Tasks Completed:" in content or "tasks completed" in content.lower():
            for line in content.split('\n'):
                if "Tasks Completed:" in line or "tasks completed" in line.lower():
                    try:
                        num_str = line.split(':')[1].strip() if ':' in line else "0"
                        briefing_data["tasks_completed"] = int(num_str)
                    except (ValueError, IndexError):
                        pass
                    break
        
        return briefing_data
    
    except Exception as e:
        dashboard_logger.error(f"Error reading briefing file: {e}")
        return None


def read_heartbeat_status() -> Dict[str, Any]:
    """
    Read the latest heartbeat entries from heartbeat.log.
    
    Returns:
        Dictionary containing heartbeat status information
    """
    heartbeat_data = {
        "status": "UNKNOWN",
        "last_beat": None,
        "beat_count": 0,
        "uptime": "Unknown",
        "pid": "Unknown",
        "recent_beats": []
    }
    
    if not HEARTBEAT_LOG.exists():
        heartbeat_data["status"] = "NO_LOG"
        return heartbeat_data
    
    try:
        recent_entries = []
        with open(HEARTBEAT_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        recent_entries.append(entry)
                    except json.JSONDecodeError:
                        # Handle human-readable log lines
                        if "System Alive" in line:
                            # Parse human-readable format
                            try:
                                parts = line.split(' - ')
                                if len(parts) >= 3:
                                    timestamp = parts[0]
                                    recent_entries.append({
                                        "timestamp": timestamp,
                                        "event_type": "heartbeat",
                                        "raw": line
                                    })
                            except Exception:
                                pass
        
        if recent_entries:
            # Get the latest heartbeat
            latest = recent_entries[-1]
            heartbeat_data["last_beat"] = latest.get("timestamp", "Unknown")
            heartbeat_data["beat_count"] = latest.get("beat_number", len(recent_entries))
            heartbeat_data["status"] = "ACTIVE"
            
            # Extract uptime if available
            details = latest.get("details", {})
            heartbeat_data["uptime"] = details.get("uptime_formatted", "Unknown")
            heartbeat_data["pid"] = details.get("process_id", "Unknown")
            
            # Store recent beats for display
            heartbeat_data["recent_beats"] = recent_entries[-5:]  # Last 5 beats
        
        return heartbeat_data
    
    except Exception as e:
        dashboard_logger.error(f"Error reading heartbeat log: {e}")
        heartbeat_data["status"] = "ERROR"
        return heartbeat_data


def check_service_health() -> Dict[str, str]:
    """
    Check the health status of background services.
    
    Returns:
        Dictionary with service names and their status
    """
    services = {}
    
    # Check Heartbeat
    if HEARTBEAT_LOG.exists():
        try:
            last_modified = datetime.fromtimestamp(HEARTBEAT_LOG.stat().st_mtime)
            time_since_update = datetime.now() - last_modified
            
            # If heartbeat log hasn't been updated in 15 minutes, consider it down
            if time_since_update.total_seconds() > 900:  # 15 minutes
                services["Heartbeat"] = "DOWN"
            else:
                services["Heartbeat"] = "RUNNING"
        except Exception:
            services["Heartbeat"] = "UNKNOWN"
    else:
        services["Heartbeat"] = "NO_LOG"
    
    # Check Gmail Watcher (by checking if inbox directory has recent files)
    inbox_dir = Path("inbox")
    if inbox_dir.exists():
        try:
            # Check if any email files exist
            email_files = list(inbox_dir.glob("email_*.json"))
            if email_files:
                services["Gmail Watcher"] = "RUNNING"
            else:
                services["Gmail Watcher"] = "IDLE"
        except Exception:
            services["Gmail Watcher"] = "UNKNOWN"
    else:
        services["Gmail Watcher"] = "NO_INBOX"
    
    # Check Autonomous Agent
    agent_log_pattern = LOGS_DIR / "autonomous_agent_*.log"
    agent_logs = list(LOGS_DIR.glob("autonomous_agent_*.log"))
    if agent_logs:
        try:
            latest_agent_log = max(agent_logs, key=lambda p: p.stat().st_mtime)
            last_modified = datetime.fromtimestamp(latest_agent_log.stat().st_mtime)
            time_since_update = datetime.now() - last_modified
            
            # If agent log hasn't been updated in 15 minutes, consider it down
            if time_since_update.total_seconds() > 900:
                services["Autonomous Agent"] = "IDLE"
            else:
                services["Autonomous Agent"] = "RUNNING"
        except Exception:
            services["Autonomous Agent"] = "UNKNOWN"
    else:
        services["Autonomous Agent"] = "NO_LOG"
    
    return services


def get_status_color(status: str) -> str:
    """Get ANSI color code for status"""
    status_colors = {
        "HEALTHY": "\033[92m",  # Green
        "ACTIVE": "\033[92m",   # Green
        "RUNNING": "\033[92m",  # Green
        "DEGRADED": "\033[93m", # Yellow
        "IDLE": "\033[93m",     # Yellow
        "CRITICAL": "\033[91m", # Red
        "DOWN": "\033[91m",     # Red
        "ERROR": "\033[91m",    # Red
        "NO_LOG": "\033[90m",   # Gray
        "UNKNOWN": "\033[90m",  # Gray
    }
    return status_colors.get(status, "\033[0m")


def print_dashboard(briefing: Optional[Dict], heartbeat: Dict, services: Dict):
    """Print the executive dashboard to console"""
    # Clear screen (works on both Windows and Unix)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Header
    print("\033[1;36m" + "=" * 70 + "\033[0m")
    print("\033[1;36m" + " " * 20 + "EXECUTIVE DASHBOARD - LIVE STATUS" + " " * 17 + "\033[0m")
    print("\033[1;36m" + "=" * 70 + "\033[0m")
    print(f"\033[90mLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    print()
    
    # System Health Overview
    print("\033[1;33m" + "-" * 70 + "\033[0m")
    print("\033[1;33m" + "SYSTEM HEALTH OVERVIEW" + "\033[0m")
    print("\033[1;33m" + "-" * 70 + "\033[0m")
    
    if briefing:
        health_status = briefing.get("health_status", "Unknown")
        color = get_status_color(health_status)
        print(f"Overall Health:     {color}{health_status}\033[0m")
        print(f"Service Failures:   {color}{briefing.get('degradation_count', 0)}\033[0m")
        print(f"Emails Processed:   {briefing.get('emails_processed', 0)}")
        print(f"Tasks Completed:    {briefing.get('tasks_completed', 0)}")
        print(f"Briefing Updated:   {briefing.get('last_modified', 'Unknown')}")
    else:
        print("Overall Health:     \033[90mNO BRIEFING AVAILABLE\033[0m")
    print()
    
    # Heartbeat Status
    print("\033[1;33m" + "-" * 70 + "\033[0m")
    print("\033[1;33m" + "HEARTBEAT MONITOR" + "\033[0m")
    print("\033[1;33m" + "-" * 70 + "\033[0m")
    
    hb_color = get_status_color(heartbeat.get("status", "UNKNOWN"))
    print(f"Status:           {hb_color}{heartbeat.get('status', 'UNKNOWN')}\033[0m")
    print(f"Last Beat:        {heartbeat.get('last_beat', 'N/A')}")
    print(f"Beat Count:       {heartbeat.get('beat_count', 0)}")
    print(f"Uptime:           {heartbeat.get('uptime', 'Unknown')}")
    print(f"Process ID:       {heartbeat.get('pid', 'Unknown')}")
    print()
    
    # Background Services Status
    print("\033[1;33m" + "-" * 70 + "\033[0m")
    print("\033[1;33m" + "BACKGROUND SERVICES" + "\033[0m")
    print("\033[1;33m" + "-" * 70 + "\033[0m")
    
    for service, status in services.items():
        color = get_status_color(status)
        status_indicator = "●" if status in ["RUNNING", "ACTIVE", "HEALTHY"] else "○"
        print(f"{status_indicator} {service:20s} {color}{status}\033[0m")
    print()
    
    # Footer
    print("\033[1;36m" + "=" * 70 + "\033[0m")
    print(f"\033[90mNext update in {DASHBOARD_INTERVAL // 60} minutes (Press Ctrl+C to stop)\033[0m")
    print("\033[1;36m" + "=" * 70 + "\033[0m")
    print()


def log_dashboard_summary(briefing: Optional[Dict], heartbeat: Dict, services: Dict):
    """Log a summary of the dashboard status to audit log"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "dashboard_update",
        "status": "success",
        "service": "Executive_Dashboard",
        "details": {
            "briefing_available": briefing is not None,
            "briefing_health": briefing.get("health_status", "N/A") if briefing else "N/A",
            "heartbeat_status": heartbeat.get("status", "UNKNOWN"),
            "heartbeat_beat_count": heartbeat.get("beat_count", 0),
            "services": services
        }
    }
    
    try:
        with open(AUDIT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        dashboard_logger.error(f"Failed to write audit log: {e}")


def main():
    """Main entry point for executive dashboard"""
    print("=" * 60)
    print("PLATINUM TIER - EXECUTIVE DASHBOARD")
    print("=" * 60)
    print(f"Starting executive dashboard...")
    print(f"Update interval: {DASHBOARD_INTERVAL} seconds")
    print(f"Reading from: {BRIEFING_FILE}")
    print(f"Monitoring: {HEARTBEAT_LOG}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    time.sleep(2)
    
    try:
        while not shutdown_requested:
            # Gather status data
            briefing = read_latest_briefing()
            heartbeat = read_heartbeat_status()
            services = check_service_health()
            
            # Display dashboard
            print_dashboard(briefing, heartbeat, services)
            
            # Log to audit
            log_dashboard_summary(briefing, heartbeat, services)
            
            dashboard_logger.info("Dashboard updated successfully")
            
            # Wait for next update
            if not shutdown_requested:
                time.sleep(DASHBOARD_INTERVAL)
    
    except KeyboardInterrupt:
        dashboard_logger.info("Keyboard interrupt received")
    except Exception as e:
        dashboard_logger.error(f"Dashboard error: {e}")
        sys.exit(1)
    finally:
        dashboard_logger.info("Executive Dashboard shutdown complete")


if __name__ == '__main__':
    main()
