"""
Background tasks for evidence collection
"""

from typing import Dict, List, Any

from database.db_setup import get_async_db
from database.services.integration_service import (
    EvidenceCollectionService,
    decrypt_integration_credentials,
)
from api.clients.aws_client import AWSAPIClient
from api.clients.okta_client import OktaAPIClient
from api.clients.google_workspace_client import GoogleWorkspaceAPIClient
from api.clients.microsoft_client import MicrosoftGraphAPIClient
from config.logging_config import get_logger

logger = get_logger(__name__)


async def execute_foundation_evidence_collection(
    collection_id: str, user_id: str, integration_map: Dict[str, Any], evidence_types: List[str]
):
    """
    Execute foundation evidence collection in background

    Args:
        collection_id: Evidence collection ID
        user_id: User who requested collection
        integration_map: Map of provider -> integration
        evidence_types: List of evidence types to collect
    """
    async for db in get_async_db():
        try:
            evidence_service = EvidenceCollectionService(db)

            # Update status to running
            await evidence_service.update_collection_status(
                collection_id=collection_id,
                status="running",
                progress_percentage=0,
                current_activity="Starting evidence collection",
            )

            logger.info(f"Starting evidence collection {collection_id} for user {user_id}")

            total_evidence_types = len(evidence_types)
            completed_types = []

            # Collect evidence from each integration
            for provider, integration in integration_map.items():
                try:
                    logger.info(f"Starting evidence collection from {provider}")

                    # Decrypt credentials
                    credentials = await decrypt_integration_credentials(integration)

                    # Create appropriate client
                    client = None
                    if provider == "aws":
                        client = AWSAPIClient(credentials)
                    elif provider == "okta":
                        client = OktaAPIClient(credentials)
                    elif provider == "google_workspace":
                        client = GoogleWorkspaceAPIClient(credentials)
                    elif provider == "microsoft_365":
                        client = MicrosoftGraphAPIClient(credentials)
                    else:
                        logger.warning(f"Unknown provider: {provider}")
                        continue

                    # Get provider-specific evidence types
                    provider_evidence_types = [
                        et for et in evidence_types if et in client.get_supported_evidence_types()
                    ]

                    if not provider_evidence_types:
                        logger.info(f"No relevant evidence types for {provider}")
                        continue

                    # Collect evidence for each type
                    for evidence_type in provider_evidence_types:
                        try:
                            await evidence_service.update_collection_status(
                                collection_id=collection_id,
                                status="running",
                                current_activity=f"Collecting {evidence_type} from {provider}",
                            )

                            # Collect the evidence
                            evidence_results = await client.collect_all_evidence()

                            # Store each evidence item
                            for evidence_result in evidence_results:
                                if evidence_result.evidence_type == evidence_type:
                                    await evidence_service.store_evidence_item(
                                        collection_id=collection_id,
                                        evidence_type=evidence_result.evidence_type,
                                        source_system=evidence_result.source_system,
                                        resource_id=evidence_result.resource_id,
                                        resource_name=evidence_result.resource_name,
                                        evidence_data=evidence_result.data,
                                        compliance_controls=evidence_result.compliance_controls,
                                        quality_score={"overall": evidence_result.quality.value}
                                        if hasattr(evidence_result.quality, "value")
                                        else {"overall": 1.0},
                                        collected_at=evidence_result.collected_at,
                                    )

                            completed_types.append(evidence_type)

                            # Update progress
                            progress = min(
                                100, int((len(completed_types) / total_evidence_types) * 100)
                            )
                            await evidence_service.update_collection_status(
                                collection_id=collection_id,
                                status="running",
                                progress_percentage=progress,
                            )

                            logger.info(f"Completed {evidence_type} collection from {provider}")

                        except Exception as e:
                            logger.error(f"Failed to collect {evidence_type} from {provider}: {e}")
                            # Continue with other evidence types
                            continue

                    await client.close()

                except Exception as e:
                    logger.error(f"Failed to collect from {provider}: {e}")
                    continue

            # Mark collection as completed
            await evidence_service.update_collection_status(
                collection_id=collection_id,
                status="completed",
                progress_percentage=100,
                current_activity="Collection completed",
            )

            logger.info(f"Evidence collection {collection_id} completed successfully")

        except Exception as e:
            logger.error(f"Evidence collection {collection_id} failed: {e}")

            # Mark as failed
            try:
                await evidence_service.update_collection_status(
                    collection_id=collection_id,
                    status="failed",
                    current_activity="Collection failed",
                    errors=[str(e)],
                )
            except Exception as update_error:
                logger.error(f"Failed to update collection status: {update_error}")

        finally:
            await db.close()
            break  # Exit the async generator
