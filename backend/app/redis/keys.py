"""Centralized Redis key name constants."""
from uuid import UUID


def refresh_token_key(user_id: UUID) -> str:
    return f"refresh:{user_id}"


def search_cache_key(query_hash: str) -> str:
    return f"search:{query_hash}"


def dashboard_cache_key(user_id: UUID) -> str:
    return f"dashboard:{user_id}"


def rate_limit_key(ip: str, minute: str) -> str:
    return f"ratelimit:{ip}:{minute}"
