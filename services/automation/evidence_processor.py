"""
Asynchronous service for processing and enriching collected evidence.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from config.logging_config import get_logger
from core.exceptions import BusinessLogicException, DatabaseException
from database.evidence_item import EvidenceItem

from .quality_scorer import QualityScorer

logger = get_logger(__name__)


class EvidenceProcessor:
    """Processes raw evidence to add scores, tags, and mappings asynchronously."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.quality_scorer = (
            QualityScorer()
        )  # QualityScorer is synchronous and CPU-bound
        self.ai_model = None  # Lazy-loaded AI model

    def process_evidence(self, evidence: EvidenceItem) -> None:
        """
        Runs the full enrichment pipeline on a single evidence item in-memory.
        The caller is responsible for committing the changes. This method is synchronous
        to allow for efficient in-memory batch processing before a final async commit.
        """
        try:
            quality_score = self.quality_scorer.calculate_score(evidence)

            raw_data_for_hash = (
                json.loads(evidence.raw_data)
                if isinstance(evidence.raw_data, str)
                else evidence.raw_data
            )

            content_to_hash = {
                "evidence_type": evidence.evidence_type,
                "description": evidence.description,
                "raw_data": raw_data_for_hash,
            }
            content_hash = hashlib.sha256(
                json.dumps(content_to_hash, sort_keys=True, default=str).encode()
            ).hexdigest()

            metadata = evidence.metadata or {}
            metadata.update(
                {
                    "quality_score": quality_score,
                    "content_hash": content_hash,
                    "processed": True,
                    "processed_at": datetime.utcnow().isoformat(),
                }
            )

            evidence.metadata = metadata
            flag_modified(evidence, "metadata")

        except (TypeError, ValueError, AttributeError, json.JSONDecodeError) as e:
            logger.error(
                f"Failed to process evidence {evidence.id} due to data error: {e}",
                exc_info=True,
            )
            metadata = evidence.metadata or {}
            metadata.update({"processed": False, "error": str(e)})
            evidence.metadata = metadata
            flag_modified(evidence, "metadata")
            # Do not re-raise to allow batch processing to continue

    async def get_processing_stats(
        self, user_id: UUID, days: int = 30
    ) -> Dict[str, Any]:
        """Retrieves processing statistics for a given user."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            stmt = select(EvidenceItem).where(
                and_(
                    EvidenceItem.user_id == user_id,
                    EvidenceItem.created_at > cutoff_date,
                    EvidenceItem.metadata["processed"].as_boolean(),
                )
            )
            result = await self.db.execute(stmt)
            processed_items = result.scalars().all()

            quality_scores = [
                item.metadata["quality_score"]
                for item in processed_items
                if item.metadata and "quality_score" in item.metadata
            ]

            avg_quality_score = (
                sum(quality_scores) / len(quality_scores) if quality_scores else 0
            )

            return {
                "processed_items": len(processed_items),
                "average_quality_score": round(avg_quality_score, 2),
                "quality_score_distribution": {
                    "high": len([s for s in quality_scores if s >= 80]),
                    "medium": len([s for s in quality_scores if 50 <= s < 80]),
                    "low": len([s for s in quality_scores if s < 50]),
                },
                "analysis_period_days": days,
            }

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while getting processing stats for user {user_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to retrieve processing statistics.") from e
        except Exception as e:
            logger.error(
                f"Unexpected error getting processing stats for user {user_id}: {e}",
                exc_info=True,
            )
            raise BusinessLogicException(
                "An unexpected error occurred while calculating statistics."
            ) from e

    def _get_ai_model(self):
        """Lazy-load AI model to avoid initialization overhead."""
        if self.ai_model is None:
            from config.ai_config import get_ai_model

            self.ai_model = get_ai_model()
        return self.ai_model

    async def _ai_classify_evidence(self, evidence: EvidenceItem) -> Dict[str, Any]:
        """
        Use AI to classify evidence type and suggest control mappings.
        Returns classification with confidence scores.
        """
        try:
            model = self._get_ai_model()

            # Prepare evidence content for analysis
            content_text = ""
            if evidence.description:
                content_text += f"Description: {evidence.description}\n"
            if hasattr(evidence, "file_path") and evidence.file_path:
                content_text += f"File: {evidence.file_path}\n"
            if evidence.evidence_type:
                content_text += f"Current Type: {evidence.evidence_type}\n"

            # Add raw data if it contains useful text
            if evidence.raw_data:
                try:
                    raw_data = (
                        json.loads(evidence.raw_data)
                        if isinstance(evidence.raw_data, str)
                        else evidence.raw_data
                    )
                    if isinstance(raw_data, dict):
                        # Extract meaningful text from raw data
                        for key, value in raw_data.items():
                            if isinstance(value, str) and len(value) > 10:
                                content_text += f"{key}: {value[:200]}...\n"
                except (json.JSONDecodeError, TypeError):
                    pass

            classification_prompt = f"""Classify this compliance evidence:

{content_text}

Classify into one of these evidence types:
- policy_document: Policies, procedures, standards
- training_record: Training materials, certificates, attendance
- audit_report: Internal/external audit findings, assessments
- technical_config: System configurations, security settings
- access_control: User access logs, permissions, reviews
- incident_report: Security incidents, breach notifications
- contract_agreement: Vendor contracts, DPAs, BAAs
- certification: Compliance certificates, attestations
- monitoring_log: System logs, monitoring data
- risk_assessment: Risk analysis, impact assessments

Suggest up to 3 relevant compliance control mappings from:
- ISO 27001 controls (format: A.X.Y.Z)
- SOC 2 controls (format: CC/PI/PR/etc.)
- GDPR articles (format: Art. X)

Provide confidence score (0-100) for classification.

Respond in this exact format:
TYPE: [evidence_type]
CONTROLS: [control1], [control2], [control3]
CONFIDENCE: [score]
REASONING: [brief explanation]"""

            response = await self._generate_ai_response(model, classification_prompt)

            # Parse AI response
            return self._parse_classification_response(response, evidence)

        except Exception as e:
            logger.warning(f"AI classification failed for evidence {evidence.id}: {e}")
            return self._fallback_classification(evidence)

    async def _generate_ai_response(self, model, prompt: str) -> str:
        """Generate AI response with proper async handling."""
        try:
            # Use asyncio to run the AI model in a thread pool to avoid blocking
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, model.generate_content, prompt)
            return response.text
        except Exception as e:
            logger.error(f"AI model generation failed: {e}")
            raise

    def _parse_classification_response(
        self, response_text: str, evidence: EvidenceItem
    ) -> Dict[str, Any]:
        """Parse structured AI classification response."""
        try:
            result = {
                "suggested_type": evidence.evidence_type or "unknown",
                "suggested_controls": [],
                "confidence": 0,
                "reasoning": "AI classification failed",
            }

            lines = response_text.strip().split("\n")
            valid_fields_found = False

            for line in lines:
                line = line.strip()

                if line.startswith("TYPE:"):
                    suggested_type = line.replace("TYPE:", "").strip()
                    if suggested_type:
                        result["suggested_type"] = suggested_type
                        valid_fields_found = True

                elif line.startswith("CONTROLS:"):
                    controls_text = line.replace("CONTROLS:", "").strip()
                    if controls_text:
                        # Split by comma and clean up
                        controls = [
                            c.strip() for c in controls_text.split(",") if c.strip()
                        ]
                        result["suggested_controls"] = controls[:3]  # Limit to 3
                        valid_fields_found = True

                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = int(line.replace("CONFIDENCE:", "").strip())
                        result["confidence"] = max(
                            0, min(100, confidence)
                        )  # Clamp to 0-100
                        valid_fields_found = True
                    except ValueError:
                        result["confidence"] = 0

                elif line.startswith("REASONING:"):
                    result["reasoning"] = line.replace("REASONING:", "").strip()
                    valid_fields_found = True

            # If no valid fields were found, use fallback classification
            if not valid_fields_found:
                return self._fallback_classification(evidence)

            return result

        except Exception as e:
            logger.warning(f"Failed to parse AI classification response: {e}")
            return self._fallback_classification(evidence)

    def _fallback_classification(self, evidence: EvidenceItem) -> Dict[str, Any]:
        """Provide rule-based fallback classification when AI fails."""
        try:
            # Use existing evidence type or try to infer from description
            evidence_name = getattr(evidence, "evidence_name", "") or ""
            description = evidence.description or ""

            name_lower = evidence_name.lower()
            desc_lower = description.lower()

            # Rule-based classification patterns
            if any(
                keyword in name_lower + desc_lower
                for keyword in ["policy", "procedure", "standard", "guideline"]
            ):
                suggested_type = "policy_document"
                controls = ["A.5.1.1", "A.5.1.2"]
            elif any(
                keyword in name_lower + desc_lower
                for keyword in ["training", "certificate", "course", "education"]
            ):
                suggested_type = "training_record"
                controls = ["A.7.2.2", "A.7.2.3"]
            elif any(
                keyword in name_lower + desc_lower
                for keyword in ["audit", "assessment", "review", "evaluation"]
            ):
                suggested_type = "audit_report"
                controls = ["A.9.2.1", "A.9.2.2"]
            elif any(
                keyword in name_lower + desc_lower
                for keyword in ["config", "setting", "technical", "system"]
            ):
                suggested_type = "technical_config"
                controls = ["A.12.6.1", "A.12.6.2"]
            elif any(
                keyword in name_lower + desc_lower
                for keyword in ["access", "permission", "user", "login"]
            ):
                suggested_type = "access_control"
                controls = ["A.9.1.1", "A.9.1.2"]
            elif any(
                keyword in name_lower + desc_lower
                for keyword in ["incident", "breach", "security event"]
            ):
                suggested_type = "incident_report"
                controls = ["A.16.1.1", "A.16.1.2"]
            elif any(
                keyword in name_lower + desc_lower
                for keyword in ["contract", "agreement", "dpa", "baa"]
            ):
                suggested_type = "contract_agreement"
                controls = ["A.15.1.1", "A.15.1.2"]
            elif any(
                keyword in name_lower + desc_lower
                for keyword in ["certificate", "certification", "attestation"]
            ):
                suggested_type = "certification"
                controls = ["A.18.1.1", "A.18.1.2"]
            elif any(
                keyword in name_lower + desc_lower
                for keyword in ["log", "monitoring", "alert", "event"]
            ):
                suggested_type = "monitoring_log"
                controls = ["A.12.4.1", "A.12.4.2"]
            elif any(
                keyword in name_lower + desc_lower
                for keyword in ["risk", "threat", "vulnerability", "impact"]
            ):
                suggested_type = "risk_assessment"
                controls = ["A.12.6.1", "A.12.6.2"]
            else:
                suggested_type = evidence.evidence_type or "unknown"
                controls = []

            return {
                "suggested_type": suggested_type,
                "suggested_controls": controls,
                "confidence": 40,  # Lower confidence for rule-based
                "reasoning": "Rule-based classification (AI unavailable)",
            }

        except Exception as e:
            logger.error(f"Fallback classification failed: {e}")
            return {
                "suggested_type": evidence.evidence_type or "unknown",
                "suggested_controls": [],
                "confidence": 0,
                "reasoning": "Classification failed",
            }

    async def enrich_evidence_with_ai(self, evidence: EvidenceItem) -> EvidenceItem:
        """
        Main method to enrich evidence with AI-powered analysis.
        Call this from evidence creation workflow.
        """
        try:
            # Get AI classification
            classification = await self._ai_classify_evidence(evidence)

            # Update evidence with AI suggestions if confidence is high enough
            if classification["confidence"] >= 60:
                # Only update if the suggested type is different and more specific
                if (
                    not evidence.evidence_type
                    or evidence.evidence_type == "unknown"
                    or classification["suggested_type"] != evidence.evidence_type
                ):
                    evidence.evidence_type = classification["suggested_type"]
                    logger.info(
                        f"Updated evidence {evidence.id} type to {classification['suggested_type']} (confidence: {classification['confidence']}%)"
                    )

            # Store AI metadata for review and audit trail
            existing_metadata = evidence.metadata or {}
            ai_metadata = {
                "ai_classification": classification,
                "ai_processed_at": datetime.utcnow().isoformat(),
                "ai_version": "gemini-2.5-flash",
            }

            # Merge with existing metadata
            existing_metadata.update(ai_metadata)
            evidence.metadata = existing_metadata
            flag_modified(evidence, "metadata")

            logger.info(
                f"AI enrichment completed for evidence {evidence.id} with confidence {classification['confidence']}%"
            )
            return evidence

        except Exception as e:
            logger.error(
                f"Failed to enrich evidence {evidence.id} with AI: {e}", exc_info=True
            )
            # Don't fail the entire process, just log the error
            return evidence

    def process_evidence_with_ai(self, evidence: EvidenceItem) -> None:
        """
        Enhanced version of process_evidence that includes AI classification.
        This is synchronous to maintain compatibility with existing workflow.
        """
        try:
            # Run original processing first
            self.process_evidence(evidence)

            # Add AI classification to metadata for async processing
            # The actual AI call will be made in a background task
            existing_metadata = evidence.metadata or {}
            existing_metadata["ai_classification_pending"] = True
            evidence.metadata = existing_metadata
            flag_modified(evidence, "metadata")

        except Exception as e:
            logger.error(
                f"Failed to process evidence {evidence.id} with AI preparation: {e}",
                exc_info=True,
            )
            # Fall back to regular processing
            self.process_evidence(evidence)
