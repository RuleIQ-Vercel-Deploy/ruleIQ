"""
Authentication and authorization decorators for service functions
"""

from functools import wraps
from typing import Callable


def authenticated(func: Callable) -> Callable:
    """
    Decorator for functions that require authentication.

    For now, this is a placeholder that allows all requests.
    In a full implementation, this would:
    1. Extract authentication token from request context
    2. Validate the token
    3. Load the user and pass it as the first argument
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # TODO: Implement actual authentication logic
        # For now, create a mock user for testing
        from uuid import uuid4

        from .user import User

        mock_user = User(id=uuid4(), email="test@example.com")
        return func(mock_user, *args, **kwargs)

    return wrapper


def public(func: Callable) -> Callable:
    """
    Decorator for public functions that don't require authentication.

    This is mainly for consistency and future extensibility.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
