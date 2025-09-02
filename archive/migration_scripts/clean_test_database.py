#!/usr/bin/env python3
"""
from __future__ import annotations

Clean test database by dropping all tables and types.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import sys
from typing import Optional


async def clean_database() -> Optional[bool]:
    """Drop all tables and types from the database."""
    db_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require",
    )
    async_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    if "sslmode=require" in async_url:
        async_url = async_url.replace("?sslmode=require", "")
        ssl_config = {"ssl": "require"}
    else:
        ssl_config = {}

    engine = create_async_engine(async_url, echo=False, connect_args=ssl_config)

    try:
        async with engine.begin() as conn:
            # Drop all tables
            print("Dropping all tables...")
            result = await conn.execute(
                text(
                    """
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
            """
                )
            )
            tables = [row[0] for row in result]

            for table in tables:
                print(f"  Dropping table: {table}")
                await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

            # Drop all custom types (enums)
            print("\nDropping all custom types...")
            result = await conn.execute(
                text(
                    """
                SELECT typname FROM pg_type
                WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                AND typtype = 'e'
            """
                )
            )
            types = [row[0] for row in result]

            for type_name in types:
                print(f"  Dropping type: {type_name}")
                await conn.execute(text(f'DROP TYPE IF EXISTS "{type_name}" CASCADE'))

            print("\nDatabase cleaned successfully!")
            return True

    except Exception as e:
        print(f"Error cleaning database: {e}")
        return False
    finally:
        await engine.dispose()


def main() -> int:
    """Run the cleanup."""
    print("Cleaning test database")
    print("=" * 50)

    success = asyncio.run(clean_database())

    print("=" * 50)
    if success:
        print("Database cleanup completed!")
        return 0
    else:
        print("Database cleanup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
