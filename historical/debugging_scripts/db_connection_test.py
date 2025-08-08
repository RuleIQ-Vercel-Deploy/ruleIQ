import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv
import os

# Load environment variables from .env.local
load_dotenv(".env.local")

# Get the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")


async def test_connection() -> None:
    """Tests the database connection and prints detailed error information."""
    print(f"Attempting to connect to database: {DATABASE_URL}")
    try:
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

        parts = urlparse(DATABASE_URL)
        query_params = parse_qs(parts.query)
        query_params.pop("sslmode", None)
        query_params.pop("channel_binding", None)
        new_query = urlencode(query_params, doseq=True)
        async_db_url = urlunparse(parts._replace(query=new_query))

        engine = create_async_engine(async_db_url, connect_args={"ssl": True})
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())
