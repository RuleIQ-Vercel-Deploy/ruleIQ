"""
User model and authentication for SQLAlchemy Access framework
"""

from typing import Optional
from uuid import UUID

from database.db_setup import SessionLocal
from database.user import User as UserModel


class User:
    """User wrapper for access control framework"""

    def __init__(self, id: UUID, email: str):
        self.id = id
        self.email = email

    @classmethod
    def from_model(cls, user_model: UserModel) -> 'User':
        """Create User from database model"""
        return cls(id=user_model.id, email=user_model.email)

    @classmethod
    def get_by_id(cls, user_id: UUID) -> Optional['User']:
        """Get user by ID"""
        db = SessionLocal()
        try:
            user_model = db.query(UserModel).filter(UserModel.id == user_id).first()
            if user_model:
                return cls.from_model(user_model)
            return None
        finally:
            db.close()

    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Get user by email"""
        db = SessionLocal()
        try:
            user_model = db.query(UserModel).filter(UserModel.email == email).first()
            if user_model:
                return cls.from_model(user_model)
            return None
        finally:
            db.close()

    def __repr__(self):
        return f"User(id={self.id}, email='{self.email}')"
