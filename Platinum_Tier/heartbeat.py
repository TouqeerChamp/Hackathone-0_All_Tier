#!/usr/bin/env python3
"""
Heartbeat Skill - Platinum Tier
================================
Background service that logs system health status at regular intervals.
Follows Gold Tier logging standards for audit compliance.

This skill runs continuously and logs a 'System Alive' message every 5 minutes
to logs/audit_logs/heartbeat.log to ensure system monitoring and health tracking.

Usage:
    python heartbeat.py

Or run in background:
    start /B python heartbeat.py

Configuration:
    HEARTBEAT_INTERVAL - Interval in seconds (default: 300 = 5 minutes)
    LOG_LEVEL - Logging level (default: INFO)
"""

import os
import sys
import time
import json
import logging
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging - Gold Tier compliant
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "300"))  # Default: 5 minutes
LOGS_DIR = Path("logs/audit_logs")

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Setup dedicated heartbeat logger
heartbeat_logger = logging.getLogger("Heartbeat")
heartbeat_logger.setLevel(getattr(logging, LOG_LEVEL))

# File handler for heartbeat.log
heartbeat_log_file = LOGS_DIR / "heartbeat.log"
file_handler = logging.FileHandler(heartbeat_log_file, encoding='utf-8')
file_handler.setLevel(getattr(logging, LOG_LEVEL))

# Console handler for visibility
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL))

# Formatter - Gold Tier standard format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

heartbeat_logger.addHandler(file_handler)
heartbeat_logger.addHandler(console_handler)

# Graceful shutdown flag
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    shutdown_requested = True
    heartbeat_logger.info(f"Received signal {signum}, initiating graceful shutdown...")


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class HeartbeatMonitor:
    """
    Heartbeat monitoring skill for Platinum Tier AI Employee.
    
    Logs system health status at regular intervals to ensure
    continuous monitoring and audit compliance.
    """

    def __init__(self, interval: int = HEARTBEAT_INTERVAL):
        """
        Initialize heartbeat monitor.
        
        Args:
            interval: Interval between heartbeats in seconds (default: 300)
        """
        self.interval = interval
        self.beat_count = 0
        self.start_time = datetime.now()
        self.last_beat_time: Optional[datetime] = None
        
        heartbeat_logger.info(f"Heartbeat monitor initialized (interval: {interval}s)")

    def get_system_health(self) -> Dict[str, Any]:
        """
        Collect current system health metrics.
        
        Returns:
            Dictionary containing system health information
        """
        current_time = datetime.now()
        uptime = current_time - self.start_time
        
        # Basic system metrics
        health_data = {
            "timestamp": current_time.isoformat(),
            "beat_number": self.beat_count + 1,
            "status": "alive",
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime),
            "interval_seconds": self.interval,
            "process_id": os.getpid(),
            "python_version": sys.version.split()[0],
            "platform": sys.platform
        }
        
        # Add memory usage if psutil is available
        try:
            import psutil
            process = psutil.Process(os.getpid())
            health_data["memory_rss_mb"] = round(process.memory_info().rss / 1024 / 1024, 2)
            health_data["memory_percent"] = round(process.memory_percent(), 2)
        except ImportError:
            health_data["memory_info"] = "psutil not installed"
        
        # Add CPU count
        health_data["cpu_count"] = os.cpu_count() or "Unknown"
        
        return health_data

    def log_heartbeat(self):
        """
        Log a single heartbeat with system health data.
        Follows Gold Tier JSON Lines audit logging format.
        """
        self.beat_count += 1
        self.last_beat_time = datetime.now()
        
        health_data = self.get_system_health()
        
        # Log in Gold Tier format (JSON Lines for audit compliance)
        audit_entry = {
            "timestamp": health_data["timestamp"],
            "event_type": "heartbeat",
            "status": "success",
            "service": "Heartbeat_Monitor",
            "beat_number": health_data["beat_number"],
            "details": health_data
        }
        
        # Write JSON Lines format to heartbeat.log
        with open(heartbeat_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
        
        # Also log human-readable message
        heartbeat_logger.info(
            f"System Alive - Beat #{health_data['beat_number']} | "
            f"Uptime: {health_data['uptime_formatted']} | "
            f"PID: {health_data['process_id']}"
        )

    def run(self):
        """
        Run the heartbeat monitor continuously.
        Logs system status every `interval` seconds until shutdown.
        """
        heartbeat_logger.info("=" * 60)
        heartbeat_logger.info("HEARTBEAT MONITOR STARTED")
        heartbeat_logger.info(f"Interval: {self.interval} seconds")
        heartbeat_logger.info(f"Log file: {heartbeat_log_file.absolute()}")
        heartbeat_logger.info("=" * 60)
        
        # Log initial heartbeat
        self.log_heartbeat()
        
        try:
            while not shutdown_requested:
                time.sleep(self.interval)
                if not shutdown_requested:
                    self.log_heartbeat()
                    
        except Exception as e:
            heartbeat_logger.error(f"Heartbeat monitor error: {e}")
            raise
        finally:
            self.log_shutdown()

    def log_shutdown(self):
        """Log shutdown event with final statistics"""
        if self.last_beat_time:
            total_runtime = self.last_beat_time - self.start_time
            heartbeat_logger.info("=" * 60)
            heartbeat_logger.info("HEARTBEAT MONITOR SHUTDOWN")
            heartbeat_logger.info(f"Total beats logged: {self.beat_count}")
            heartbeat_logger.info(f"Total runtime: {total_runtime}")
            heartbeat_logger.info("=" * 60)
            
            # Log final audit entry
            final_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "heartbeat_shutdown",
                "status": "success",
                "service": "Heartbeat_Monitor",
                "details": {
                    "total_beats": self.beat_count,
                    "total_runtime_seconds": total_runtime.total_seconds(),
                    "last_beat": self.last_beat_time.isoformat()
                }
            }
            with open(heartbeat_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(final_entry, ensure_ascii=False) + '\n')


def main():
    """Main entry point for heartbeat skill"""
    print("=" * 60)
    print("PLATINUM TIER - HEARTBEAT SKILL")
    print("=" * 60)
    print(f"Starting heartbeat monitor...")
    print(f"Interval: {HEARTBEAT_INTERVAL} seconds")
    print(f"Log file: {heartbeat_log_file.absolute()}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    monitor = HeartbeatMonitor(interval=HEARTBEAT_INTERVAL)
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        heartbeat_logger.info("Keyboard interrupt received")
    except Exception as e:
        heartbeat_logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
