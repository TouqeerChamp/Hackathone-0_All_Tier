#!/usr/bin/env python3
"""
Odoo Client - Gold Tier
=======================
Agent Skill for connecting to Odoo ERP via XML-RPC.
Provides graceful degradation when Odoo is offline.

Usage:
    from odoo_client import get_odoo_summary

    summary = get_odoo_summary()
    print(summary)
"""

import xmlrpc.client
import logging
from typing import Dict, Any, Optional
from graceful_degradation import with_graceful_degradation, FallbackMethod


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OdooClient")


# Odoo connection details
ODOO_URL = "http://localhost:8069"
ODOO_DB = "ai_employee_db"
ODOO_USER = "touqeerchamp@gmail.com"
ODOO_PASS = "OdooAdmin123"


@with_graceful_degradation(
    service_name="Odoo ERP",
    fallbacks=[FallbackMethod.LOCAL_CACHE, FallbackMethod.SKIP_WITH_LOG],
    cache=True
)
def get_odoo_summary() -> Dict[str, Any]:
    """
    Get a summary of key metrics from Odoo.

    Returns:
        Dictionary containing:
        - customers_count: Number of customers (res.partner)
        - sales_orders_count: Number of sales orders (sale.order)
        - source: Where the data came from ('odoo', 'cache', or 'skipped')
        - note: Additional information about the data source

    Raises:
        xmlrpc.client.Fault: If Odoo authentication fails
        ConnectionError: If Odoo server is unreachable
    """
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

    # Authenticate
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})

    if not uid:
        raise ConnectionError("Odoo authentication failed - invalid credentials")

    logger.info(f"Successfully connected to Odoo as user ID: {uid}")

    # Count customers (res.partner with is_customer=True or customer_rank > 0)
    customers_count = models.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        'res.partner', 'search_count',
        [[['customer_rank', '>', 0]]]
    )

    # Count sales orders
    sales_orders_count = models.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        'sale.order', 'search_count',
        [[]]  # All records
    )

    summary = {
        "customers_count": customers_count,
        "sales_orders_count": sales_orders_count,
        "source": "odoo",
        "note": "Live data from Odoo ERP"
    }

    logger.info(f"Odoo summary: {customers_count} customers, {sales_orders_count} sales orders")

    return summary


def get_odoo_connection() -> Optional[Dict[str, Any]]:
    """
    Get raw Odoo connection objects for advanced operations.

    Returns:
        Dictionary with 'common', 'models', and 'uid' keys, or None if connection fails
    """
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})

        if not uid:
            logger.error("Odoo authentication failed")
            return None

        return {
            "common": common,
            "models": models,
            "uid": uid,
            "db": ODOO_DB,
            "password": ODOO_PASS
        }
    except Exception as e:
        logger.error(f"Failed to connect to Odoo: {e}")
        return None


def execute_odoo_query(
    model: str,
    method: str,
    args: list = None,
    kwargs: dict = None
) -> Any:
    """
    Execute a generic query on Odoo.

    Args:
        model: Odoo model name (e.g., 'res.partner', 'sale.order')
        method: Model method to call (e.g., 'search', 'read', 'create')
        args: Positional arguments for the method
        kwargs: Keyword arguments for the method

    Returns:
        Result from Odoo or None if failed
    """
    connection = get_odoo_connection()
    if not connection:
        return None

    try:
        return connection["models"].execute_kw(
            connection["db"],
            connection["uid"],
            connection["password"],
            model,
            method,
            args or [],
            kwargs or {}
        )
    except Exception as e:
        logger.error(f"Odoo query failed: {e}")
        return None


# Export main functions
__all__ = [
    "get_odoo_summary",
    "get_odoo_connection",
    "execute_odoo_query",
    "ODOO_URL",
    "ODOO_DB",
    "ODOO_USER"
]
