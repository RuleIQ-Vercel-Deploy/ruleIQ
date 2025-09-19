from __future__ import annotations

import os
from urllib.parse import urlparse, urlunparse

from celery import Celery


def _db_index_url(url: str, index: int) -> str:
    """
    Return the same Redis URL with a different database index.
    """
    try:
        parsed = urlparse(url)
        # Keep scheme and netloc, replace path with /{index}
        return urlunparse((parsed.scheme, parsed.netloc, f"/{index}", "", "", ""))
    except Exception:
        return url


def _resolve_broker_and_backend() -> tuple[str, str]:
    """
    Resolve Celery broker and backend URLs with robust fallbacks:
    - Prefer explicit CELERY_BROKER_URL and CELERY_RESULT_BACKEND
    - Fall back to REDIS_URL with db 1 (broker) and 2 (backend)
    - Fall back to in-cluster defaults pointing at 'redis' service
    """
    broker = os.getenv("CELERY_BROKER_URL")
    backend = os.getenv("CELERY_RESULT_BACKEND")

    redis_url = os.getenv("REDIS_URL")
    if not broker and redis_url:
        broker = _db_index_url(redis_url, 1)
    if not backend and redis_url:
        backend = _db_index_url(redis_url, 2)

    if not broker:
        # default to docker-compose service 'redis' on db 1
        redis_password = os.getenv("REDIS_PASSWORD", "")
        auth = f":{redis_password}@" if redis_password else ""
        broker = f"redis://{auth}redis:6379/1"

    if not backend:
        # default to docker-compose service 'redis' on db 2
        redis_password = os.getenv("REDIS_PASSWORD", "")
        auth = f":{redis_password}@" if redis_password else ""
        backend = f"redis://{auth}redis:6379/2"

    return broker, backend


broker_url, result_backend = _resolve_broker_and_backend()

celery_app = Celery("ruleiq", broker=broker_url, backend=result_backend)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_pool_limit=10,
    broker_heartbeat=30,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="ruleiq.ping")
def ping() -> str:
    """
    Simple sanity task to verify worker connectivity.
    """
    return "pong"