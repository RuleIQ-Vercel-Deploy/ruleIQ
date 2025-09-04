"""
Database dependency for FastAPI endpoints.

This module re-exports the async session provider from the core database setup
to maintain a consistent dependency structure for the API layer.
"""

from database.db_setup import get_async_db

# The get_async_db function is re-exported here to be used as a FastAPI dependency.
# This avoids the API layer having to reach deep into the database layer for session management.
__all__ = ["get_async_db"]
