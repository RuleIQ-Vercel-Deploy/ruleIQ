from __future__ import annotations

import os
import sys
import time
from urllib.parse import urlparse

import psycopg2
from psycopg2 import OperationalError


def main() -> int:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is not set; skipping wait_for_db.")
        return 0

    parsed = urlparse(db_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    user = parsed.username or ""
    dbname = parsed.path.lstrip("/") or ""
    print(f"Waiting for database {dbname} at {host}:{port} ...")

    timeout_seconds = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
    deadline = time.time() + timeout_seconds
    last_error: str | None = None

    while time.time() < deadline:
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            print("Database is ready.")
            return 0
        except OperationalError as e:
            last_error = str(e)
            time.sleep(2)

    print(f"Timed out waiting for database after {timeout_seconds}s. Last error: {last_error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())