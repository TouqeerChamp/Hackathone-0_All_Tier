#!/usr/bin/env python3
"""
CEO Briefer - Gold Tier Phase 3
================================
Agent Skill for generating weekly CEO briefings with business health,
marketing pulse, and system integrity reports.

Usage:
    python ceo_briefer.py

Or import as a module:
    from ceo_briefer import generate_ceo_briefing

    briefing = generate_ceo_briefing()
    print(briefing['markdown'])
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from odoo_client import get_odoo_summary
from social_media.social_manager import get_social_summary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CEOBriefer")

# Constants
LOGS_DIR = Path("logs")
AUDIT_LOGS_DIR = LOGS_DIR / "audit_logs"
BRIEFING_OUTPUT_DIR = Path(".")  # Save briefings in root directory


class SystemIntegrityChecker:
    """Check system logs for service degradation events"""

    def __init__(self, audit_log_dir: Path = AUDIT_LOGS_DIR):
        self.audit_log_dir = audit_log_dir
        self.degradation_events: List[Dict[str, Any]] = []
        self.fallback_events: List[Dict[str, Any]] = []

    def check_logs(self, hours: int = 168) -> Dict[str, Any]:
        """
        Check audit logs for service degradation events in the last N hours.

        Args:
            hours: Number of hours to look back (default: 168 = 1 week)

        Returns:
            Dictionary containing system integrity report
        """
        self.degradation_events = []
        self.fallback_events = []

        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Check all log files in audit_logs directory
        log_files = list(self.audit_log_dir.glob("*.log"))

        for log_file in log_files:
            self._parse_log_file(log_file, cutoff_time)

        # Check graceful degradation log specifically
        degradation_log = self.audit_log_dir / "graceful_degradation.log"
        if degradation_log.exists():
            self._parse_degradation_log(degradation_log, cutoff_time)

        return {
            "check_period": {
                "hours": hours,
                "cutoff_time": cutoff_time.isoformat(),
                "checked_at": datetime.now().isoformat()
            },
            "degradation_events": self.degradation_events,
            "fallback_events": self.fallback_events,
            "total_issues": len(self.degradation_events) + len(self.fallback_events),
            "health_status": self._calculate_health_status()
        }

    def _parse_log_file(self, log_file: Path, cutoff_time: datetime):
        """Parse a JSON Lines log file for events"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        timestamp_str = entry.get("timestamp", "")

                        if timestamp_str:
                            timestamp = datetime.fromisoformat(timestamp_str)

                            if timestamp >= cutoff_time:
                                # Check for service degradation indicators
                                status = entry.get("status", "")
                                event_type = entry.get("event_type", "")

                                if status == "unhealthy" or event_type == "failure":
                                    self.degradation_events.append({
                                        "timestamp": timestamp_str,
                                        "service": entry.get("service", "Unknown"),
                                        "event_type": event_type,
                                        "status": status,
                                        "details": entry.get("details", {}),
                                        "log_file": log_file.name,
                                        "line": line_num
                                    })

                                # Check for fallback usage
                                if event_type == "fallback_success":
                                    self.fallback_events.append({
                                        "timestamp": timestamp_str,
                                        "service": entry.get("service", "Unknown"),
                                        "fallback_method": entry.get("details", {}).get("method", "unknown"),
                                        "log_file": log_file.name,
                                        "line": line_num
                                    })

                    except json.JSONDecodeError:
                        # Skip non-JSON lines (plain text logs)
                        continue

        except Exception as e:
            logger.warning(f"Failed to parse log file {log_file}: {e}")

    def _parse_degradation_log(self, log_file: Path, cutoff_time: datetime):
        """Specifically parse graceful degradation log"""
        self._parse_log_file(log_file, cutoff_time)

    def _calculate_health_status(self) -> str:
        """Calculate overall system health status"""
        if len(self.degradation_events) == 0 and len(self.fallback_events) == 0:
            return "HEALTHY"
        elif len(self.degradation_events) <= 2 and len(self.fallback_events) <= 5:
            return "DEGRADED"
        else:
            return "CRITICAL"


def generate_ai_recommendations(
    odoo_data: Dict[str, Any],
    social_data: Dict[str, Any],
    system_data: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Generate AI-powered recommendations for the CEO.

    Args:
        odoo_data: Business health data from Odoo
        social_data: Marketing pulse data from social media
        system_data: System integrity data

    Returns:
        List of recommendation dictionaries
    """
    recommendations = []

    # Business Health Recommendations
    customers = odoo_data.get("customers_count", 0)
    sales = odoo_data.get("sales_orders_count", 0)

    if customers == 0:
        recommendations.append({
            "priority": "HIGH",
            "category": "Business Growth",
            "recommendation": "Customer database is empty. Prioritize customer onboarding and data migration to Odoo ERP.",
            "action": "Import existing customer data or begin manual entry immediately."
        })
    elif customers < 10:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Business Growth",
            "recommendation": f"Customer base is small ({customers} customers). Focus on customer acquisition strategies.",
            "action": "Review sales pipeline and marketing campaigns to increase customer intake."
        })
    else:
        recommendations.append({
            "priority": "LOW",
            "category": "Business Growth",
            "recommendation": f"Healthy customer base ({customers} customers). Consider upselling and retention programs.",
            "action": "Implement customer loyalty programs and analyze churn metrics."
        })

    if sales == 0:
        recommendations.append({
            "priority": "HIGH",
            "category": "Revenue",
            "recommendation": "No sales orders recorded. Immediate attention needed for sales pipeline.",
            "action": "Review active leads and convert pending opportunities to sales orders."
        })
    elif sales < customers:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Revenue",
            "recommendation": f"Sales conversion rate may be low ({sales} sales vs {customers} customers).",
            "action": "Analyze customer engagement and identify conversion bottlenecks."
        })

    # Marketing Recommendations
    total_posts = social_data.get("statistics", {}).get("total_posts", 0)
    fb_posts = social_data.get("statistics", {}).get("facebook_posts", 0)
    ig_posts = social_data.get("statistics", {}).get("instagram_posts", 0)
    tw_posts = social_data.get("statistics", {}).get("twitter_posts", 0)

    if total_posts == 0:
        recommendations.append({
            "priority": "HIGH",
            "category": "Marketing",
            "recommendation": "No social media activity detected. Establish a content calendar immediately.",
            "action": "Create weekly posting schedule across Facebook, Instagram, and Twitter."
        })
    elif total_posts < 5:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Marketing",
            "recommendation": f"Low social media activity ({total_posts} posts). Increase content frequency.",
            "action": "Aim for at least 3-5 posts per week per platform for optimal engagement."
        })
    else:
        recommendations.append({
            "priority": "LOW",
            "category": "Marketing",
            "recommendation": f"Good social media activity ({total_posts} posts). Consider analytics review.",
            "action": "Analyze engagement metrics and optimize posting times."
        })

    # Platform-specific recommendations
    if fb_posts == 0:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Marketing - Facebook",
            "recommendation": "No Facebook posts. Facebook remains a key channel for B2B engagement.",
            "action": "Schedule Facebook posts highlighting company updates and industry insights."
        })

    if ig_posts == 0:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Marketing - Instagram",
            "recommendation": "No Instagram posts. Visual content can boost brand awareness.",
            "action": "Create visual content showcasing products, team, and company culture."
        })

    if tw_posts == 0:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Marketing - Twitter",
            "recommendation": "No Twitter activity. Twitter is essential for real-time engagement.",
            "action": "Post industry news, company updates, and engage with relevant conversations."
        })

    # System Integrity Recommendations
    system_health = system_data.get("health_status", "UNKNOWN")
    degradation_count = len(system_data.get("degradation_events", []))
    fallback_count = len(system_data.get("fallback_events", []))

    if system_health == "CRITICAL":
        recommendations.append({
            "priority": "HIGH",
            "category": "System Integrity",
            "recommendation": f"Critical system health: {degradation_count} service failures detected.",
            "action": "Immediate investigation required. Review logs and restore affected services."
        })
    elif system_health == "DEGRADED":
        recommendations.append({
            "priority": "MEDIUM",
            "category": "System Integrity",
            "recommendation": f"System operating in degraded mode. {fallback_count} fallbacks used.",
            "action": "Schedule maintenance window to address service issues."
        })
    else:
        recommendations.append({
            "priority": "LOW",
            "category": "System Integrity",
            "recommendation": "All systems operating normally. Continue monitoring.",
            "action": "Maintain current monitoring practices and review logs weekly."
        })

    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recommendations


def generate_markdown_briefing(
    odoo_data: Dict[str, Any],
    social_data: Dict[str, Any],
    system_data: Dict[str, Any],
    recommendations: List[Dict[str, str]]
) -> str:
    """
    Generate the CEO briefing in Markdown format.

    Args:
        odoo_data: Business health data
        social_data: Marketing pulse data
        system_data: System integrity data
        recommendations: AI-generated recommendations

    Returns:
        Formatted Markdown string
    """
    now = datetime.now()
    briefing_date = now.strftime("%Y-%m-%d")
    briefing_time = now.strftime("%H:%M:%S")

    # Calculate metrics
    customers = odoo_data.get("customers_count", 0)
    sales = odoo_data.get("sales_orders_count", 0)
    odoo_source = odoo_data.get("source", "unknown")

    total_posts = social_data.get("statistics", {}).get("total_posts", 0)
    fb_posts = social_data.get("statistics", {}).get("facebook_posts", 0)
    ig_posts = social_data.get("statistics", {}).get("instagram_posts", 0)
    tw_posts = social_data.get("statistics", {}).get("twitter_posts", 0)

    system_health = system_data.get("health_status", "UNKNOWN")
    degradation_count = len(system_data.get("degradation_events", []))
    fallback_count = len(system_data.get("fallback_events", []))

    # Build Markdown
    md = f"""# 📊 CEO Weekly Briefing

**Generated:** {briefing_date} at {briefing_time}  
**Prepared by:** AI Employee (Gold Tier Phase 3)

---

## 🏢 Business Health: Odoo ERP Stats

| Metric | Value | Data Source |
|--------|-------|-------------|
| **Total Customers** | {customers} | {odoo_source} |
| **Sales Orders** | {sales} | {odoo_source} |

### Analysis
"""

    if customers == 0:
        md += "- ⚠️ **Customer Database Empty**: No customers recorded in Odoo ERP.\n"
    elif customers < 50:
        md += f"- 📈 **Growing Base**: {customers} customers currently in system.\n"
    else:
        md += f"- ✅ **Established Base**: {customers} customers actively tracked.\n"

    if sales == 0:
        md += "- ⚠️ **No Sales Orders**: Sales pipeline requires immediate attention.\n"
    else:
        md += f"- 💼 **Sales Activity**: {sales} sales orders recorded.\n"

    md += f"""
---

## 📣 Marketing Pulse: Social Media Activity

| Platform | Posts (Last 24h) | Status |
|----------|------------------|--------|
| **Facebook** | {fb_posts} | {'✅ Active' if fb_posts > 0 else '⚠️ Inactive'} |
| **Instagram** | {ig_posts} | {'✅ Active' if ig_posts > 0 else '⚠️ Inactive'} |
| **Twitter** | {tw_posts} | {'✅ Active' if tw_posts > 0 else '⚠️ Inactive'} |
| **Total** | **{total_posts}** | {'✅ Good' if total_posts >= 5 else '⚠️ Low'} |

### Recent Posts Summary
"""

    recent_posts = social_data.get("recent_posts", [])
    if recent_posts:
        md += "\n"
        for post in recent_posts[:5]:  # Show last 5 posts
            platform = post.get("platform", "unknown").title()
            created = post.get("created_at", "Unknown")[:10]
            content = post.get("content_summary", "No content")
            md += f"- **{platform}** ({created}): {content}\n"
    else:
        md += "- No recent posts found. Consider establishing a content calendar.\n"

    md += f"""
---

## 🔧 System Integrity: Errors & Fallbacks

**Overall Health Status:** `{system_health}`

### Service Degradation Events
"""

    degradation_events = system_data.get("degradation_events", [])
    if degradation_events:
        md += f"\n**{len(degradation_events)} degradation events detected:**\n\n"
        md += "| Timestamp | Service | Event Type | Status |\n"
        md += "|-----------|---------|------------|--------|\n"
        for event in degradation_events[:10]:  # Limit to 10
            ts = event.get("timestamp", "Unknown")[:19]
            service = event.get("service", "Unknown")
            event_type = event.get("event_type", "Unknown")
            status = event.get("status", "Unknown")
            md += f"| {ts} | {service} | {event_type} | {status} |\n"
    else:
        md += "\n✅ No service degradation events detected.\n"

    md += f"""
### Fallback Usage
"""

    fallback_events = system_data.get("fallback_events", [])
    if fallback_events:
        md += f"\n**{len(fallback_events)} fallback operations used:**\n\n"
        md += "| Timestamp | Service | Fallback Method |\n"
        md += "|-----------|---------|----------------|\n"
        for event in fallback_events[:10]:  # Limit to 10
            ts = event.get("timestamp", "Unknown")[:19]
            service = event.get("service", "Unknown")
            method = event.get("fallback_method", "Unknown")
            md += f"| {ts} | {service} | {method} |\n"
    else:
        md += "\n✅ No fallback operations required.\n"

    md += f"""
---

## 💡 AI-Generated Recommendations for Mohammad Touqeer

"""

    high_priority = [r for r in recommendations if r["priority"] == "HIGH"]
    medium_priority = [r for r in recommendations if r["priority"] == "MEDIUM"]
    low_priority = [r for r in recommendations if r["priority"] == "LOW"]

    if high_priority:
        md += "### 🔴 HIGH Priority\n\n"
        for rec in high_priority:
            md += f"**{rec['category']}**: {rec['recommendation']}\n\n"
            md += f"> **Action:** {rec['action']}\n\n"

    if medium_priority:
        md += "### 🟡 MEDIUM Priority\n\n"
        for rec in medium_priority:
            md += f"**{rec['category']}**: {rec['recommendation']}\n\n"
            md += f"> **Action:** {rec['action']}\n\n"

    if low_priority:
        md += "### 🟢 LOW Priority\n\n"
        for rec in low_priority:
            md += f"**{rec['category']}**: {rec['recommendation']}\n\n"
            md += f"> **Action:** {rec['action']}\n\n"

    md += f"""
---

## 📋 Executive Summary

**Business Health:** {'⚠️ Needs Attention' if customers == 0 or sales == 0 else '✅ Operational'}  
**Marketing Activity:** {'⚠️ Low' if total_posts < 5 else '✅ Active'}  
**System Status:** {'🔴 Critical' if system_health == 'CRITICAL' else '🟡 Degraded' if system_health == 'DEGRADED' else '🟢 Healthy'}

**Key Takeaways:**
"""

    # Generate key takeaways
    takeaways = []
    if customers == 0:
        takeaways.append("- Urgent: Populate customer database in Odoo")
    if sales == 0:
        takeaways.append("- Urgent: Activate sales pipeline")
    if total_posts == 0:
        takeaways.append("- Urgent: Begin social media content strategy")
    if system_health == "CRITICAL":
        takeaways.append("- Urgent: Address system failures")

    if not takeaways:
        takeaways.append("- Continue current operations")
        takeaways.append("- Monitor growth metrics weekly")

    md += "\n".join(takeaways)
    md += "\n\n---\n\n*This briefing was automatically generated by your AI Employee.*\n"
    md += "*For questions or improvements, contact the development team.*\n"

    return md


def generate_ceo_briefing() -> Dict[str, Any]:
    """
    Main function to generate a complete CEO briefing.

    Returns:
        Dictionary containing:
        - odoo_data: Business health data
        - social_data: Marketing pulse data
        - system_data: System integrity data
        - recommendations: AI recommendations
        - markdown: Formatted briefing string
        - file_path: Path to saved briefing file
    """
    logger.info("Starting CEO briefing generation...")

    # 1. Get Odoo data
    logger.info("Fetching Odoo ERP data...")
    try:
        odoo_data = get_odoo_summary()
    except Exception as e:
        logger.error(f"Failed to get Odoo data: {e}")
        odoo_data = {
            "customers_count": 0,
            "sales_orders_count": 0,
            "source": "error",
            "note": f"Failed to connect to Odoo: {str(e)}",
            "error": str(e)
        }

    # 2. Get social media data
    logger.info("Fetching social media data...")
    try:
        social_data = get_social_summary(hours=24)
    except Exception as e:
        logger.error(f"Failed to get social media data: {e}")
        social_data = {
            "summary_period": {"hours": 24},
            "statistics": {
                "total_posts": 0,
                "by_platform": {"facebook": 0, "instagram": 0, "twitter": 0}
            },
            "recent_posts": [],
            "error": str(e)
        }

    # 3. Check system integrity
    logger.info("Checking system integrity...")
    integrity_checker = SystemIntegrityChecker()
    system_data = integrity_checker.check_logs(hours=168)  # Last week

    # 4. Generate recommendations
    logger.info("Generating AI recommendations...")
    recommendations = generate_ai_recommendations(odoo_data, social_data, system_data)

    # 5. Generate Markdown briefing
    logger.info("Generating Markdown briefing...")
    markdown_content = generate_markdown_briefing(
        odoo_data, social_data, system_data, recommendations
    )

    # 6. Save briefing to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"CEO_Briefing_{timestamp}.md"
    file_path = BRIEFING_OUTPUT_DIR / filename

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info(f"Briefing saved to: {file_path}")
    except Exception as e:
        logger.error(f"Failed to save briefing: {e}")
        file_path = None

    # Also update CEO_Weekly_Briefing.md (latest version)
    latest_file = BRIEFING_OUTPUT_DIR / "CEO_Weekly_Briefing.md"
    try:
        with open(latest_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info(f"Latest briefing saved to: {latest_file}")
    except Exception as e:
        logger.error(f"Failed to save latest briefing: {e}")

    return {
        "odoo_data": odoo_data,
        "social_data": social_data,
        "system_data": system_data,
        "recommendations": recommendations,
        "markdown": markdown_content,
        "file_path": str(file_path),
        "latest_file": str(latest_file)
    }


def main():
    """Main entry point for CLI usage"""
    print("=" * 70)
    print("CEO BRIEFING GENERATOR - Gold Tier Phase 3")
    print("=" * 70)
    print()

    result = generate_ceo_briefing()

    print()
    print("=" * 70)
    print("BRIEFING SUMMARY")
    print("=" * 70)
    print()

    # Business Health
    print("🏢 BUSINESS HEALTH:")
    print(f"   • Customers: {result['odoo_data'].get('customers_count', 0)}")
    print(f"   • Sales Orders: {result['odoo_data'].get('sales_orders_count', 0)}")
    print(f"   • Data Source: {result['odoo_data'].get('source', 'unknown')}")
    print()

    # Marketing Pulse
    print("📣 MARKETING PULSE:")
    stats = result['social_data'].get('statistics', {})
    print(f"   • Total Posts (24h): {stats.get('total_posts', 0)}")
    print(f"   • Facebook: {stats.get('facebook_posts', 0)}")
    print(f"   • Instagram: {stats.get('instagram_posts', 0)}")
    print(f"   • Twitter: {stats.get('twitter_posts', 0)}")
    print()

    # System Integrity
    print("🔧 SYSTEM INTEGRITY:")
    print(f"   • Health Status: {result['system_data'].get('health_status', 'UNKNOWN')}")
    print(f"   • Degradation Events: {len(result['system_data'].get('degradation_events', []))}")
    print(f"   • Fallbacks Used: {len(result['system_data'].get('fallback_events', []))}")
    print()

    # Recommendations
    print("💡 TOP RECOMMENDATIONS:")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"   {i}. [{rec['priority']}] {rec['category']}: {rec['recommendation'][:60]}...")
    print()

    print("=" * 70)
    print(f"✅ Briefing saved to: {result['latest_file']}")
    print("=" * 70)

    return result


if __name__ == "__main__":
    main()
