#!/usr/bin/env python3
"""
Database initialization script for ComplianceGPT

This script creates all database tables and optionally populates them with default data.
Run this script after setting up your DATABASE_URL environment variable.
"""

import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import Base, engine
from services.framework_service import initialize_default_frameworks


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def populate_default_data():
    """Populate database with default frameworks and data"""
    print("Populating default data...")
    try:
        initialize_default_frameworks()
        print("✓ Default frameworks initialized")
        return True
    except Exception as e:
        print(f"✗ Error populating default data: {e}")
        return False


def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    try:
        from database.db_setup import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def main():
    """Main initialization function"""
    print("ComplianceGPT Database Initialization")
    print("=" * 40)

    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("✗ DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL in your .env file")
        return False

    print(f"Database URL: {os.getenv('DATABASE_URL')}")
    print()

    # Test connection
    if not test_connection():
        return False

    # Create tables
    if not create_tables():
        return False

    # Populate default data
    if not populate_default_data():
        return False

    print()
    print("✓ Database initialization completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
