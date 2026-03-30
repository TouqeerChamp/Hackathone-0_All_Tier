"""
Social Media Manager Package - Gold Tier Phase 2
================================================
Agent Skills for social media automation.
"""

from .social_manager import (
    post_to_facebook,
    post_to_instagram,
    post_to_twitter,
    get_social_summary,
    SocialMediaAuditLogger,
    POST_HISTORY_FILE
)

__all__ = [
    "post_to_facebook",
    "post_to_instagram",
    "post_to_twitter",
    "get_social_summary",
    "SocialMediaAuditLogger",
    "POST_HISTORY_FILE"
]
