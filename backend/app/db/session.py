"""Async session dependency - re-export get_db from base for clarity."""
from app.db.base import get_db

__all__ = ["get_db"]
