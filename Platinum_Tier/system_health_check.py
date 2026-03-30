#!/usr/bin/env python3
"""
System Health Check - Gold Tier
================================
Checks the health status of critical system components:
- Local Odoo server connectivity
- MCP server availability
- Core service status

Logs all health check results to logs/audit_logs/
"""

import os
import sys
import json
import socket
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


# Configuration
AUDIT_LOG_DIR = Path("logs/audit_logs")
DEFAULT_ODOO_URL = "http://localhost:8069"
DEFAULT_ODOO_TIMEOUT = 5  # seconds
DEFAULT_MCP_TIMEOUT = 3  # seconds


def ensure_audit_log_dir():
    """Ensure the audit logs directory exists."""
    AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_audit_event(event_type: str, status: str, details: Dict[str, Any]):
    """
    Log an audit event to the audit_logs directory.
    
    Args:
        event_type: Type of event (e.g., 'health_check', 'service_status')
        status: Status of the event (e.g., 'success', 'warning', 'error')
        details: Dictionary containing event details
    """
    ensure_audit_log_dir()
    
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "status": status,
        "details": details
    }
    
    # Create daily audit log file
    log_file = AUDIT_LOG_DIR / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Also print to console for immediate visibility
    status_icon = {"success": "✓", "warning": "⚠", "error": "✗"}.get(status, "•")
    print(f"[{timestamp}] {status_icon} [{event_type.upper()}] {details.get('message', '')}")


def check_odoo_server(url: str = DEFAULT_ODOO_URL, timeout: int = DEFAULT_ODOO_TIMEOUT) -> Dict[str, Any]:
    """
    Check if the local Odoo server is running.
    
    Args:
        url: Odoo server URL
        timeout: Request timeout in seconds
    
    Returns:
        Dictionary with health check results
    """
    result = {
        "service": "Odoo Server",
        "url": url,
        "status": "unknown",
        "response_time_ms": None,
        "message": ""
    }
    
    try:
        start_time = datetime.now()
        
        # Try to connect to the Odoo server
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            result["response_time_ms"] = round(elapsed, 2)
            result["status"] = "healthy"
            result["message"] = f"Odoo server is running (HTTP {response.status})"
            
    except urllib.error.HTTPError as e:
        result["status"] = "warning"
        result["message"] = f"Odoo server responded with HTTP error: {e.code}"
        
    except urllib.error.URLError as e:
        result["status"] = "error"
        result["message"] = f"Cannot connect to Odoo server: {e.reason}"
        
    except socket.timeout:
        result["status"] = "error"
        result["message"] = f"Connection to Odoo server timed out after {timeout}s"
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Unexpected error checking Odoo server: {str(e)}"
    
    # Log the health check result
    log_audit_event(
        event_type="health_check",
        status="success" if result["status"] == "healthy" else "error",
        details=result
    )
    
    return result


def check_mcp_servers() -> Dict[str, Any]:
    """
    Check the status of configured MCP servers.
    This is a placeholder that checks if MCP configuration exists.
    
    Returns:
        Dictionary with MCP server health status
    """
    result = {
        "service": "MCP Servers",
        "status": "unknown",
        "servers": [],
        "message": ""
    }
    
    try:
        # Check for MCP configuration
        mcp_config_path = Path("mcp.json")
        if not mcp_config_path.exists():
            result["status"] = "warning"
            result["message"] = "MCP configuration file (mcp.json) not found"
            log_audit_event("health_check", "warning", result)
            return result
        
        with open(mcp_config_path, 'r', encoding='utf-8') as f:
            mcp_config = json.load(f)
        
        servers = mcp_config.get("mcpServers", {})
        
        if not servers:
            result["status"] = "warning"
            result["message"] = "No MCP servers configured in mcp.json"
            log_audit_event("health_check", "warning", result)
            return result
        
        # Check each configured server (placeholder - actual implementation would ping each server)
        for server_name, server_config in servers.items():
            server_status = {
                "name": server_name,
                "configured": True,
                "status": "unknown",  # Would be determined by actual health check
                "message": "Configuration found (health check not implemented)"
            }
            result["servers"].append(server_status)
        
        result["status"] = "healthy"
        result["message"] = f"Found {len(servers)} configured MCP server(s)"
        
    except json.JSONDecodeError as e:
        result["status"] = "error"
        result["message"] = f"Invalid JSON in mcp.json: {str(e)}"
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Error checking MCP servers: {str(e)}"
    
    log_audit_event("health_check", "success" if result["status"] == "healthy" else "error", result)
    return result


def check_core_services() -> Dict[str, Any]:
    """
    Check the status of core Python services/scripts.
    
    Returns:
        Dictionary with core services health status
    """
    result = {
        "service": "Core Services",
        "status": "healthy",
        "services": [],
        "message": ""
    }
    
    core_scripts = [
        "inbox_scanner.py",
        "gmail_watcher.py",
        "create_plans.py",
        "linkedin_automation.py",
        "briefing.py"
    ]
    
    missing_scripts = []
    
    for script in core_scripts:
        script_path = Path(script)
        service_status = {
            "name": script,
            "exists": script_path.exists(),
            "status": "healthy" if script_path.exists() else "missing"
        }
        result["services"].append(service_status)
        
        if not script_path.exists():
            missing_scripts.append(script)
            result["status"] = "warning"
    
    if missing_scripts:
        result["message"] = f"Missing scripts: {', '.join(missing_scripts)}"
    else:
        result["message"] = "All core scripts present"
    
    log_audit_event("health_check", "success" if result["status"] == "healthy" else "warning", result)
    return result


def run_full_health_check() -> Dict[str, Any]:
    """
    Run a comprehensive health check of all system components.
    
    Returns:
        Dictionary with overall system health status
    """
    print("=" * 60)
    print("SYSTEM HEALTH CHECK")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Ensure audit log directory exists
    ensure_audit_log_dir()
    
    # Run all health checks
    odoo_status = check_odoo_server()
    mcp_status = check_mcp_servers()
    core_status = check_core_services()
    
    # Determine overall system health
    all_checks = [odoo_status, mcp_status, core_status]
    
    if all(check["status"] == "healthy" for check in all_checks):
        overall_status = "healthy"
        overall_message = "All systems operational"
    elif any(check["status"] == "error" for check in all_checks):
        overall_status = "degraded"
        overall_message = "One or more critical services are not operational"
    else:
        overall_status = "warning"
        overall_message = "Some services have warnings but system is functional"
    
    # Log overall status
    log_audit_event(
        event_type="system_health",
        status=overall_status,
        details={
            "message": overall_message,
            "odoo": odoo_status,
            "mcp": mcp_status,
            "core": core_status
        }
    )
    
    # Print summary
    print("-" * 60)
    print("SUMMARY")
    print("-" * 60)
    print(f"Overall Status: {overall_status.upper()}")
    print(f"Message: {overall_message}")
    print()
    print("Component Status:")
    for check in all_checks:
        icon = {"healthy": "✓", "warning": "⚠", "error": "✗", "unknown": "?"}.get(
            check["status"], "•"
        )
        print(f"  {icon} {check['service']}: {check['message']}")
    
    print()
    print(f"Audit log saved to: {AUDIT_LOG_DIR.absolute()}")
    print("=" * 60)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "overall_status": overall_status,
        "message": overall_message,
        "components": {
            "odoo": odoo_status,
            "mcp": mcp_status,
            "core": core_status
        }
    }


if __name__ == "__main__":
    run_full_health_check()
