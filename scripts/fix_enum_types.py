#!/usr/bin/env python3
"""Script to fix enum type issues in the database."""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main() -> None:
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        sys.exit(1)

    # Create engine
    engine = create_engine(database_url)

    try:
        with engine.connect() as conn:
            # Drop the enum type if it exists
            print("Dropping existing integrationstatus enum type...")
            conn.execute(text("DROP TYPE IF EXISTS integrationstatus CASCADE"))
            conn.commit()
            print("Successfully dropped integrationstatus enum type")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
