import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from .db_setup import Base  # Import Base from our new db_setup.py


class User(Base):
  __tablename__ = "users"
  id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  email = Column(String, nullable=False, unique=True) # Added nullable=False and unique=True as common for emails
  hashed_password = Column(String, nullable=False)
  is_active = Column(Boolean, default=True)
  created_at = Column(DateTime, default=datetime.utcnow)
