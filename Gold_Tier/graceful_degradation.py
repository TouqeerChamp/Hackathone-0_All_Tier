#!/usr/bin/env python3
"""
Graceful Degradation Utility - Gold Tier
=========================================
Provides fallback mechanisms when MCP servers or external services fail.
Instead of crashing, the system logs errors and attempts alternative methods.

Usage:
    from graceful_degradation import GracefulDegradation, FallbackMethod
    
    # Create instance with fallback methods
    degrader = GracefulDegradation(
        service_name="Google Search",
        fallbacks=[FallbackMethod.LOCAL_CACHE, FallbackMethod.MANUAL_RESEARCH]
    )
    
    # Use in try-except blocks
    try:
        result = call_mcp_service()
    except Exception as e:
        result = degrader.handle_failure(e, query="search terms")
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Any, Dict, List, Optional, Callable


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GracefulDegradation")


class FallbackMethod(Enum):
    """Available fallback methods for graceful degradation."""
    LOCAL_CACHE = "local_cache"  # Use cached results
    MANUAL_RESEARCH = "manual_research"  # Generate manual research template
    BASIC_SEARCH = "basic_search"  # Use basic urllib search (if available)
    SKIP_WITH_LOG = "skip_with_log"  # Log and skip the operation
    DEFAULT_RESPONSE = "default_response"  # Return a safe default response


class ServiceHealthStatus(Enum):
    """Health status for services."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class GracefulDegradation:
    """
    Handles graceful degradation when MCP servers or external services fail.
    
    Attributes:
        service_name: Name of the service being monitored
        fallbacks: List of fallback methods to try in order
        cache_dir: Directory for caching results
        max_retries: Maximum number of retry attempts
    """
    
    def __init__(
        self,
        service_name: str,
        fallbacks: Optional[List[FallbackMethod]] = None,
        cache_dir: str = "logs/audit_logs/cache",
        max_retries: int = 2
    ):
        self.service_name = service_name
        self.fallbacks = fallbacks or [FallbackMethod.SKIP_WITH_LOG]
        self.cache_dir = Path(cache_dir)
        self.max_retries = max_retries
        self.failure_count = 0
        self.last_error: Optional[Exception] = None
        self.status = ServiceHealthStatus.UNKNOWN
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Audit log file
        self.audit_log = Path("logs/audit_logs/graceful_degradation.log")
        
        self._log_event("initialized", {
            "service": service_name,
            "fallbacks": [f.value for f in self.fallbacks]
        })
    
    def _log_event(self, event_type: str, details: Dict[str, Any]):
        """Log an event to the audit log."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "service": self.service_name,
                "event_type": event_type,
                "status": self.status.value,
                "details": details
            }
            
            with open(self.audit_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
            
            # Also log via standard logging
            log_msg = f"[{self.service_name}] {event_type}: {details.get('message', str(details))}"
            if event_type == "failure":
                logger.warning(log_msg)
            elif event_type == "recovery":
                logger.info(log_msg)
            else:
                logger.info(log_msg)
                
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
    
    def _get_cache_key(self, **kwargs) -> str:
        """Generate a cache key from kwargs."""
        key_parts = [f"{k}={v}" for k, v in sorted(kwargs.items())]
        return "_".join(key_parts).replace(" ", "_").replace("/", "_")
    
    def _get_cache_file(self, key: str) -> Path:
        """Get the cache file path for a given key."""
        return self.cache_dir / f"{key}.json"
    
    def read_from_cache(self, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Try to read a result from cache.
        
        Returns:
            Cached result if found and not expired, None otherwise
        """
        cache_key = self._get_cache_key(**kwargs)
        cache_file = self._get_cache_file(cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check if cache is still valid (e.g., within 24 hours)
            cached_time = datetime.fromisoformat(cached_data.get("cached_at", ""))
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            
            if age_hours > 24:
                logger.info(f"Cache expired for {cache_key} (age: {age_hours:.1f}h)")
                return None
            
            self._log_event("cache_hit", {"key": cache_key, "age_hours": age_hours})
            return cached_data.get("result")
            
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def write_to_cache(self, result: Dict[str, Any], **kwargs):
        """Write a result to cache."""
        cache_key = self._get_cache_key(**kwargs)
        cache_file = self._get_cache_file(cache_key)
        
        try:
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "key": cache_key,
                "result": result
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
                
            self._log_event("cache_write", {"key": cache_key})
            
        except Exception as e:
            logger.warning(f"Error writing to cache: {e}")
    
    def clear_cache(self):
        """Clear all cached results."""
        try:
            if self.cache_dir.exists():
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
                self._log_event("cache_cleared", {})
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def handle_failure(
        self,
        error: Exception,
        original_function: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Handle a service failure by trying fallback methods.
        
        Args:
            error: The exception that was raised
            original_function: Name of the function that failed
            **kwargs: Additional context for fallback methods
        
        Returns:
            Result from fallback method or None
        """
        self.failure_count += 1
        self.last_error = error
        self.status = ServiceHealthStatus.UNHEALTHY
        
        self._log_event("failure", {
            "error": str(error),
            "error_type": type(error).__name__,
            "function": original_function,
            "failure_count": self.failure_count,
            "kwargs": kwargs
        })
        
        # Try each fallback method in order
        for fallback in self.fallbacks:
            try:
                result = self._execute_fallback(fallback, error, **kwargs)
                if result is not None:
                    self.status = ServiceHealthStatus.DEGRADED
                    return result
            except Exception as fallback_error:
                logger.warning(f"Fallback {fallback.value} failed: {fallback_error}")
                continue
        
        # All fallbacks failed
        self._log_event("all_fallbacks_failed", {
            "fallbacks_tried": [f.value for f in self.fallbacks]
        })
        
        return None
    
    def _execute_fallback(
        self,
        fallback: FallbackMethod,
        error: Exception,
        **kwargs
    ) -> Any:
        """Execute a specific fallback method."""
        
        if fallback == FallbackMethod.LOCAL_CACHE:
            cached_result = self.read_from_cache(**kwargs)
            if cached_result:
                return {
                    "source": "cache",
                    "data": cached_result,
                    "note": "Served from cache due to service unavailability"
                }
            return None
        
        elif fallback == FallbackMethod.MANUAL_RESEARCH:
            return self._generate_manual_research_template(**kwargs)
        
        elif fallback == FallbackMethod.BASIC_SEARCH:
            return self._basic_web_search(**kwargs)
        
        elif fallback == FallbackMethod.SKIP_WITH_LOG:
            self._log_event("skipped", {
                "reason": "Skip with log fallback selected",
                "original_error": str(error)
            })
            return {
                "source": "skipped",
                "data": [],
                "note": "Operation skipped due to service unavailability"
            }
        
        elif fallback == FallbackMethod.DEFAULT_RESPONSE:
            return self._get_default_response(**kwargs)
        
        return None
    
    def _generate_manual_research_template(self, **kwargs) -> Dict[str, Any]:
        """Generate a template for manual research."""
        query = kwargs.get("query", "Unknown topic")
        
        template = {
            "source": "manual_research_template",
            "data": [
                {
                    "title": f"Manual Research Required: {query}",
                    "link": "#manual-research",
                    "snippet": f"This research topic requires manual investigation: '{query}'. "
                              f"Please search for relevant information and update the plan manually."
                }
            ],
            "note": "Manual research template generated due to service unavailability",
            "requires_manual_action": True,
            "suggested_search_terms": [
                query,
                f"{query} best practices",
                f"{query} 2026",
                f"{query} guide"
            ]
        }
        
        self._log_event("fallback_success", {
            "method": "manual_research_template",
            "query": query
        })
        
        return template
    
    def _basic_web_search(self, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Perform a basic web search using urllib as a fallback.
        This is a simple fallback that doesn't require MCP.
        """
        query = kwargs.get("query", "")
        num_results = kwargs.get("num_results", 5)
        
        if not query:
            return None
        
        # Note: This is a placeholder. In a real implementation,
        # you might use a different search API or service.
        self._log_event("fallback_attempt", {
            "method": "basic_web_search",
            "query": query,
            "note": "Basic web search not implemented - requires API configuration"
        })
        
        return None
    
    def _get_default_response(self, **kwargs) -> Dict[str, Any]:
        """Return a safe default response."""
        return {
            "source": "default",
            "data": [],
            "note": "Default response returned due to service unavailability"
        }
    
    def record_success(self, result: Any, **kwargs):
        """Record a successful operation to update health status."""
        if self.status != ServiceHealthStatus.HEALTHY:
            self._log_event("recovery", {
                "message": "Service recovered",
                "previous_status": self.status.value
            })
        
        self.status = ServiceHealthStatus.HEALTHY
        self.failure_count = 0
        self.last_error = None
        
        # Cache the successful result
        if kwargs:  # Only cache if we have kwargs for the cache key
            self.write_to_cache(result, **kwargs)
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get a status report for this service."""
        return {
            "service": self.service_name,
            "status": self.status.value,
            "failure_count": self.failure_count,
            "last_error": str(self.last_error) if self.last_error else None,
            "fallbacks_configured": [f.value for f in self.fallbacks],
            "cache_dir": str(self.cache_dir)
        }


# Convenience functions for common scenarios

def with_graceful_degradation(
    service_name: str,
    fallbacks: Optional[List[FallbackMethod]] = None,
    cache: bool = True
):
    """
    Decorator for adding graceful degradation to functions.
    
    Usage:
        @with_graceful_degradation("Google Search", cache=True)
        def google_search(query, num_results=5):
            # Your implementation here
            pass
    """
    def decorator(func: Callable) -> Callable:
        degrader = GracefulDegradation(
            service_name=service_name,
            fallbacks=fallbacks or [FallbackMethod.SKIP_WITH_LOG],
            cache_dir="logs/audit_logs/cache" if cache else None
        )
        
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                degrader.record_success(result, **kwargs)
                return result
            except Exception as e:
                return degrader.handle_failure(
                    error=e,
                    original_function=func.__name__,
                    **kwargs
                )
        
        wrapper.degrader = degrader  # Expose degrader for status checks
        return wrapper
    
    return decorator


# Export main classes and functions
__all__ = [
    "GracefulDegradation",
    "FallbackMethod",
    "ServiceHealthStatus",
    "with_graceful_degradation"
]
