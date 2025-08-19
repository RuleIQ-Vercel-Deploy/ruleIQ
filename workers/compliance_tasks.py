"""
Celery background tasks for compliance scoring and monitoring, with async support.
"""

import asyncio
from typing import Any, Dict

from celery.utils.log import get_task_logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from celery_app import celery_app
from core.exceptions import (
    ApplicationException,
    BusinessLogicException,
    DatabaseException,
)
from database.db_setup import get_async_db
from database.business_profile import BusinessProfile
from services.readiness_service import generate_readiness_assessment

logger = get_task_logger(__name__)

# --- Async Helper Functions ---


async def _update_all_compliance_scores_async() -> Dict[str, Any]:
    """Async helper to update compliance scores for all business profiles."""
    updated_count = 0
    failed_count = 0
    total_profiles = 0
    async for db in get_async_db():
        try:
            profiles_res = await db.execute(select(BusinessProfile))
            profiles = profiles_res.scalars().all()
            total_profiles = len(profiles)

            for profile in profiles:
                try:
                    readiness_data = await generate_readiness_assessment(profile.id, db)
                    logger.debug(
                        (
                            f"Updated compliance score for profile {profile.id}: "
                            f"{readiness_data.get('overall_score', 0)}"
                        )
                    )
                    updated_count += 1
                except ApplicationException as e:
                    logger.error(
                        f"Failed to update compliance score for profile {profile.id}: {e}",
                        exc_info=True,
                    )
                    failed_count += 1

            logger.info(
                (
                    f"Finished compliance score update. Total: {total_profiles}, "
                    f"Updated: {updated_count}, Failed: {failed_count}"
                )
            )
            return {
                "status": "completed",
                "total_profiles": total_profiles,
                "updated_count": updated_count,
                "failed_count": failed_count,
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching profiles: {e}", exc_info=True)
            raise DatabaseException(
                "Failed to fetch business profiles for compliance scoring."
            ) from e


async def _check_compliance_alerts_async() -> Dict[str, Any]:
    """Async helper to check for compliance issues requiring attention."""
    alerts = []
    async for db in get_async_db():
        try:
            profiles_res = await db.execute(select(BusinessProfile))
            profiles = profiles_res.scalars().all()

            for profile in profiles:
                try:
                    readiness_data = await generate_readiness_assessment(profile.id, db)
                    if readiness_data.get("overall_score", 100) < 70:
                        alert = {
                            "profile_id": str(profile.id),
                            "score": readiness_data["overall_score"],
                            "message": "Compliance score is below threshold.",
                        }
                        alerts.append(alert)
                        logger.warning(
                            (
                                f"Compliance alert for profile {profile.id}: "
                                f"Score is {readiness_data['overall_score']}"
                            )
                        )
                except ApplicationException as e:
                    logger.warning(
                        f"Could not check compliance alerts for profile {profile.id}: {e}",
                        exc_info=True,
                    )

            return {"status": "completed", "alerts_count": len(alerts), "alerts": alerts}
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching profiles for alert check: {e}", exc_info=True
            )
            raise DatabaseException("Failed to fetch business profiles for alert check.") from e


# --- Celery Tasks ---


@celery_app.task(
    bind=True,
    autoretry_for=(DatabaseException, Exception),
    retry_kwargs={
        "max_retries": 5,
        "countdown": 90,  # Start with 90 seconds
    },
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    rate_limit="3/m",  # 3 compliance score updates per minute
)
def update_all_compliance_scores(self):
    """Updates compliance scores for all business profiles by running the async helper."""
    logger.info("Starting compliance score updates for all profiles")
    try:
        return asyncio.run(_update_all_compliance_scores_async())
    except BusinessLogicException as e:
        logger.error(
            f"Compliance score update failed with a business logic error. Not retrying. Error: {e}",
            exc_info=True,
        )
    except DatabaseException as e:
        logger.error(
            "Compliance score update failed with a database error. Retrying...", exc_info=True
        )
        self.retry(exc=e)
    except Exception as e:
        logger.critical("Unexpected error in compliance score update. Retrying...", exc_info=True)
        self.retry(exc=e)


@celery_app.task(
    bind=True,
    autoretry_for=(DatabaseException, Exception),
    retry_kwargs={
        "max_retries": 5,
        "countdown": 60,  # Start with 60 seconds
    },
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    rate_limit="5/m",  # 5 alert checks per minute
)
def check_compliance_alerts(self):
    """Checks for compliance issues that require immediate attention by running the async helper."""
    logger.info("Checking for compliance alerts")
    try:
        return asyncio.run(_check_compliance_alerts_async())
    except BusinessLogicException as e:
        logger.error(
            f"Compliance alert check failed with a business logic error. Not retrying. Error: {e}",
            exc_info=True,
        )
    except DatabaseException as e:
        logger.error(
            "Compliance alert check failed with a database error. Retrying...", exc_info=True
        )
        self.retry(exc=e)
    except Exception as e:
        logger.critical("Unexpected error in compliance alert check. Retrying...", exc_info=True)
        self.retry(exc=e)
