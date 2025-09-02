"""
Service for calculating a quality score for each piece of evidence.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config.logging_config import get_logger
from core.exceptions import BusinessLogicException
from database.evidence_item import EvidenceItem

logger = get_logger(__name__)


class QualityScorer:
    """Calculates a quality score (0-100) for evidence."""

    def __init__(self) -> None:
        """Initialize the quality scorer with scoring weights."""
        self.weights = {
            "completeness": 0.30,
            "freshness": 0.25,
            "relevance": 0.25,
            "verifiability": 0.20,
        }
        self.ai_model = None  # Lazy-loaded AI model

        # Enhanced AI scoring weights
        self.ai_weights = {
            "completeness": 0.20,
            "clarity": 0.15,
            "currency": 0.15,
            "verifiability": 0.15,
            "relevance": 0.15,
            "sufficiency": 0.20,
        }

    def calculate_score(self, evidence: EvidenceItem) -> float:
        """
        Calculates a weighted quality score based on completeness, freshness,
        relevance, and verifiability.
        """
        try:
            scores = {
                "completeness": self._score_completeness(evidence),
                "freshness": self._score_freshness(evidence),
                "relevance": self._score_relevance(evidence),
                "verifiability": self._score_verifiability(evidence),
            }

            total_score = sum(
                scores[aspect] * self.weights[aspect] for aspect in scores
            )
            return round(min(max(total_score, 0.0), 100.0), 2)

        except (ValueError, TypeError, KeyError) as e:
            logger.warning(
                f"Could not calculate quality score for evidence {evidence.id} due to data issue: {e}",
                exc_info=True,
            )
            return 50.0  # Return neutral score on error

    def _score_completeness(self, evidence: EvidenceItem) -> float:
        """Score based on how complete the evidence content is."""
        try:
            if not isinstance(evidence.content, dict):
                return 10.0  # Low score if content is not a dictionary

            required_fields = ["name", "description", "source", "timestamp"]
            present_fields = sum(
                1 for field in required_fields if evidence.content.get(field)
            )

            # Additional check for meaningful content
            if len(evidence.content.get("description", "")) < 20:
                present_fields -= 0.5  # Penalize short descriptions

            return (present_fields / len(required_fields)) * 100
        except (TypeError, AttributeError) as e:
            logger.warning(
                f"Completeness scoring failed for evidence {evidence.id}: {e}"
            )
            return 20.0

    def _score_freshness(self, evidence: EvidenceItem) -> float:
        """Score based on the age of the evidence."""
        try:
            evidence_date = evidence.collected_at
            age = datetime.utcnow() - evidence_date

            if age < timedelta(days=30):
                return 100.0
            if age < timedelta(days=90):
                return 80.0
            if age < timedelta(days=180):
                return 50.0
            return 20.0
        except TypeError as e:
            logger.warning(f"Freshness scoring failed for evidence {evidence.id}: {e}")
            return 0.0

    def _score_relevance(self, evidence: EvidenceItem) -> float:
        """Score based on relevance to compliance frameworks (mock)."""
        # In a real implementation, this would involve NLP or keyword matching.
        try:
            if not isinstance(evidence.content, dict):
                return 10.0

            relevance_score = 50.0  # Base score
            description = evidence.content.get("description", "").lower()
            if any(
                keyword in description
                for keyword in ["audit", "control", "security", "compliance"]
            ):
                relevance_score += 25.0
            if evidence.control_id:
                relevance_score += 25.0

            return min(relevance_score, 100.0)
        except AttributeError as e:
            logger.warning(f"Relevance scoring failed for evidence {evidence.id}: {e}")
            return 20.0

    def _score_verifiability(self, evidence: EvidenceItem) -> float:
        """Score based on the trustworthiness of the evidence source."""
        try:
            if not isinstance(evidence.content, dict):
                return 10.0

            source = evidence.content.get("source", "unknown").lower()
            if source in ["api_integration", "sso_logs", "cloud_audit_logs"]:
                return 100.0
            if source == "user_upload":
                return 60.0
            return 30.0
        except AttributeError as e:
            logger.warning(
                f"Verifiability scoring failed for evidence {evidence.id}: {e}"
            )
            return 20.0

    def get_score_breakdown(self, evidence: EvidenceItem) -> Dict[str, Any]:
        """Provides a detailed breakdown of the quality score."""
        try:
            scores = {
                "completeness": self._score_completeness(evidence),
                "freshness": self._score_freshness(evidence),
                "relevance": self._score_relevance(evidence),
                "verifiability": self._score_verifiability(evidence),
            }
            total_score = self.calculate_score(evidence)

            return {
                "total_score": total_score,
                "breakdown": scores,
                "weights": self.weights,
            }
        except (ValueError, TypeError) as e:
            raise BusinessLogicException(
                f"Failed to get score breakdown for evidence {evidence.id}"
            ) from e

    def calculate_batch_scores(
        self, evidence_items: List[EvidenceItem]
    ) -> Dict[str, Any]:
        """Calculates quality scores for multiple evidence items."""
        if not evidence_items:
            return {"total_items": 0, "average_score": 0.0, "score_distribution": {}}

        try:
            scores = [self.calculate_score(item) for item in evidence_items]
            average_score = sum(scores) / len(scores)

            score_ranges = {
                "excellent": (90, 100),
                "good": (80, 89.99),
                "acceptable": (70, 79.99),
                "poor": (50, 69.99),
                "very_poor": (0, 49.99),
            }

            distribution = {
                range_name: {"count": 0, "percentage": 0.0}
                for range_name in score_ranges
            }
            for score in scores:
                for range_name, (min_s, max_s) in score_ranges.items():
                    if min_s <= score <= max_s:
                        distribution[range_name]["count"] += 1
                        break

            for range_name in distribution:
                count = distribution[range_name]["count"]
                distribution[range_name]["percentage"] = round(
                    count / len(scores) * 100, 1
                )

            return {
                "total_items": len(evidence_items),
                "average_score": round(average_score, 2),
                "score_distribution": distribution,
            }
        except Exception as e:
            logger.error(f"Error in batch scoring: {e}", exc_info=True)
            raise BusinessLogicException("Failed to calculate batch scores.") from e

    def _get_ai_model(self):
        """Lazy-load AI model to avoid initialization overhead."""
        if self.ai_model is None:
            from config.ai_config import get_ai_model

            self.ai_model = get_ai_model()
        return self.ai_model

    async def calculate_enhanced_score(self, evidence: EvidenceItem) -> Dict[str, Any]:
        """
        Calculate evidence quality score with AI enhancement.
        Combines traditional algorithmic scoring with AI-powered analysis.
        """
        try:
            # Get traditional algorithmic scores
            traditional_scores = self._calculate_traditional_scores(evidence)

            # Get AI quality analysis
            ai_analysis = await self._ai_quality_analysis(evidence)

            # Combine scores with weighted approach
            final_score = self._combine_traditional_and_ai_scores(
                traditional_scores, ai_analysis
            )

            # Determine scoring method based on whether AI analysis succeeded
            scoring_method = (
                "traditional_fallback" if "error" in ai_analysis else "enhanced_ai"
            )

            # Set confidence based on scoring method
            if scoring_method == "traditional_fallback":
                confidence = 30  # Higher confidence for traditional fallback
            else:
                confidence = ai_analysis.get("ai_confidence", 50)

            return {
                "overall_score": final_score,
                "traditional_scores": traditional_scores,
                "ai_analysis": ai_analysis,
                "scoring_method": scoring_method,
                "confidence": confidence,
                "analysis_timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Enhanced scoring failed for evidence {evidence.id}: {e}",
                exc_info=True,
            )
            # Fall back to traditional scoring
            traditional_score = self.calculate_score(evidence)
            return {
                "overall_score": traditional_score,
                "traditional_scores": {"total": traditional_score},
                "ai_analysis": {"error": "AI analysis unavailable"},
                "scoring_method": "traditional_fallback",
                "confidence": 30,
                "analysis_timestamp": datetime.utcnow().isoformat(),
            }

    async def _ai_quality_analysis(self, evidence: EvidenceItem) -> Dict[str, Any]:
        """
        Use AI to analyze evidence quality across multiple dimensions.
        Returns detailed quality assessment with scores and recommendations.
        """
        try:
            model = self._get_ai_model()

            # Prepare content for AI analysis
            content_summary = self._prepare_content_for_analysis(evidence)

            quality_prompt = f"""Analyze the quality of this compliance evidence:

{content_summary}

Rate each dimension from 0-100:
- COMPLETENESS: How complete is the information? Are key details present?
- CLARITY: How clear and understandable is the content?
- CURRENCY: How current/up-to-date is this evidence?
- VERIFIABILITY: How easily can this evidence be verified or audited?
- RELEVANCE: How relevant is this to compliance requirements?
- SUFFICIENCY: Is this evidence sufficient to demonstrate compliance?

Also identify:
- STRENGTHS: What makes this evidence good?
- WEAKNESSES: What could be improved?
- RECOMMENDATIONS: Specific improvement suggestions

Format response as:
COMPLETENESS: [score]
CLARITY: [score]
CURRENCY: [score]
VERIFIABILITY: [score]
RELEVANCE: [score]
SUFFICIENCY: [score]
OVERALL: [average score]
STRENGTHS: [list strengths]
WEAKNESSES: [list weaknesses]
RECOMMENDATIONS: [list recommendations]"""

            # Use asyncio to run the AI model in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, model.generate_content, quality_prompt
            )

            # Parse AI response
            return self._parse_quality_response(response.text)

        except Exception as e:
            logger.warning(
                f"AI quality analysis failed for evidence {evidence.id}: {e}"
            )
            fallback_result = self._fallback_quality_analysis(evidence)
            # Add error indicator to mark this as a fallback result
            fallback_result["error"] = "AI analysis unavailable"
            return fallback_result

    def _prepare_content_for_analysis(self, evidence: EvidenceItem) -> str:
        """Prepare evidence content for AI analysis."""
        content_parts = []

        if evidence.evidence_name:
            content_parts.append(f"Name: {evidence.evidence_name}")

        if evidence.description:
            content_parts.append(f"Description: {evidence.description}")

        if evidence.evidence_type:
            content_parts.append(f"Type: {evidence.evidence_type}")

        if hasattr(evidence, "control_reference") and evidence.control_reference:
            content_parts.append(f"Control Reference: {evidence.control_reference}")

        if evidence.collected_at:
            content_parts.append(f"Collected: {evidence.collected_at.isoformat()}")

        # Add raw data if it contains useful text
        if evidence.raw_data:
            try:
                raw_data = (
                    json.loads(evidence.raw_data)
                    if isinstance(evidence.raw_data, str)
                    else evidence.raw_data
                )
                if isinstance(raw_data, dict):
                    for key, value in raw_data.items():
                        if (
                            isinstance(value, str) and len(value) > 2
                        ):  # Include short values like 'pdf'
                            content_parts.append(f"{key}: {value[:200]}...")
            except (json.JSONDecodeError, TypeError):
                pass

        return "\n".join(content_parts) if content_parts else "No content available"

    def _parse_quality_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured AI quality analysis response."""
        try:
            result = {
                "scores": {},
                "overall_score": 0,
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "ai_confidence": 50,
            }

            lines = response_text.strip().split("\n")
            current_section = None

            for line in lines:
                line = line.strip()

                # Parse scores
                if ":" in line and any(
                    dimension in line.upper()
                    for dimension in [
                        "COMPLETENESS",
                        "CLARITY",
                        "CURRENCY",
                        "VERIFIABILITY",
                        "RELEVANCE",
                        "SUFFICIENCY",
                        "OVERALL",
                    ]
                ):
                    parts = line.split(":", 1)
                    dimension = parts[0].strip().upper()
                    try:
                        score = int(re.search(r"\d+", parts[1]).group())
                        score = max(0, min(100, score))  # Clamp to 0-100

                        if dimension == "OVERALL":
                            result["overall_score"] = score
                        else:
                            result["scores"][dimension.lower()] = score
                    except (ValueError, AttributeError):
                        continue

                # Parse sections
                elif line.upper().startswith("STRENGTHS:"):
                    current_section = "strengths"
                    content = line.split(":", 1)[1].strip()
                    if content:
                        result["strengths"].append(content)
                elif line.upper().startswith("WEAKNESSES:"):
                    current_section = "weaknesses"
                    content = line.split(":", 1)[1].strip()
                    if content:
                        result["weaknesses"].append(content)
                elif line.upper().startswith("RECOMMENDATIONS:"):
                    current_section = "recommendations"
                    content = line.split(":", 1)[1].strip()
                    if content:
                        result["recommendations"].append(content)
                elif current_section and line and not line.startswith("-"):
                    result[current_section].append(line)

            # Calculate overall score if not provided
            if result["overall_score"] == 0 and result["scores"]:
                result["overall_score"] = sum(result["scores"].values()) / len(
                    result["scores"]
                )

            # If no scores were parsed, return fallback result
            if not result["scores"]:
                return self._fallback_quality_analysis(None)

            # Set confidence based on completeness of analysis
            if (
                len(result["scores"]) >= 4
                and result["strengths"]
                and result["weaknesses"]
            ):
                result["ai_confidence"] = 85
            elif len(result["scores"]) >= 3:
                result["ai_confidence"] = 70
            else:
                result["ai_confidence"] = 50

            return result

        except Exception as e:
            logger.warning(f"Failed to parse AI quality response: {e}")
            return self._fallback_quality_analysis(None)

    def _fallback_quality_analysis(
        self, evidence: Optional[EvidenceItem]
    ) -> Dict[str, Any]:
        """Provide rule-based fallback quality analysis when AI fails."""
        try:
            if evidence is None:
                return {
                    "scores": {
                        "completeness": 30,
                        "clarity": 30,
                        "currency": 30,
                        "verifiability": 30,
                        "relevance": 30,
                        "sufficiency": 30,
                    },
                    "overall_score": 30,
                    "strengths": ["Evidence exists"],
                    "weaknesses": ["Analysis unavailable"],
                    "recommendations": ["Retry analysis when AI service is available"],
                    "ai_confidence": 0,
                }

            # Basic rule-based analysis
            scores = {}
            strengths = []
            weaknesses = []
            recommendations = []

            # Completeness analysis
            if evidence.evidence_name and evidence.description:
                scores["completeness"] = 70
                strengths.append("Has name and description")
            else:
                scores["completeness"] = 30
                weaknesses.append("Missing name or description")
                recommendations.append("Add complete name and description")

            # Clarity analysis (based on description length and content)
            if evidence.description and len(evidence.description) > 50:
                scores["clarity"] = 60
                strengths.append("Adequate description length")
            else:
                scores["clarity"] = 30
                weaknesses.append("Description too brief")
                recommendations.append("Provide more detailed description")

            # Currency analysis (based on collection date)
            if evidence.collected_at:
                age_days = (datetime.utcnow() - evidence.collected_at).days
                if age_days < 30:
                    scores["currency"] = 90
                    strengths.append("Recently collected evidence")
                elif age_days < 90:
                    scores["currency"] = 70
                else:
                    scores["currency"] = 40
                    weaknesses.append("Evidence is getting old")
                    recommendations.append(
                        "Consider updating or re-collecting evidence"
                    )
            else:
                scores["currency"] = 30
                weaknesses.append("No collection date available")

            # Default scores for other dimensions
            scores.update({"verifiability": 50, "relevance": 50, "sufficiency": 50})

            overall_score = sum(scores.values()) / len(scores)

            return {
                "scores": scores,
                "overall_score": round(overall_score, 1),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": recommendations,
                "ai_confidence": 20,  # Low confidence for rule-based
            }

        except Exception as e:
            logger.error(f"Fallback quality analysis failed: {e}")
            return {
                "scores": {
                    "completeness": 30,
                    "clarity": 30,
                    "currency": 30,
                    "verifiability": 30,
                    "relevance": 30,
                    "sufficiency": 30,
                },
                "overall_score": 30,
                "strengths": [],
                "weaknesses": ["Analysis failed"],
                "recommendations": ["Manual review required"],
                "ai_confidence": 0,
            }

    def _calculate_traditional_scores(self, evidence: EvidenceItem) -> Dict[str, float]:
        """Calculate traditional algorithmic quality scores."""
        scores = {}

        # Completeness score (based on filled fields)
        completeness_factors = [
            evidence.evidence_name is not None,
            evidence.description is not None and len(evidence.description) > 10,
            hasattr(evidence, "control_reference")
            and bool(getattr(evidence, "control_reference", None)),
            hasattr(evidence, "file_path")
            and bool(getattr(evidence, "file_path", None)),
            evidence.evidence_type is not None,
        ]
        scores["completeness"] = (
            sum(int(factor) for factor in completeness_factors)
            / len(completeness_factors)
        ) * 100

        # Freshness score (based on age)
        if evidence.collected_at:
            age_days = (datetime.utcnow() - evidence.collected_at).days
            scores["freshness"] = max(
                0, 100 - (age_days * 2)
            )  # Decrease 2 points per day
        else:
            scores["freshness"] = 50

        # Content quality score (based on description length and keywords)
        if evidence.description:
            desc_length = len(evidence.description)
            # Optimal description length: 100-500 characters
            if 100 <= desc_length <= 500:
                scores["content_quality"] = 100
            elif desc_length < 100:
                scores["content_quality"] = (desc_length / 100) * 100
            else:
                scores["content_quality"] = max(50, 100 - ((desc_length - 500) / 20))
        else:
            scores["content_quality"] = 20

        # Relevance score (based on keywords and type)
        relevance_score = 50  # Base score
        if evidence.description:
            desc_lower = evidence.description.lower()
            if any(
                keyword in desc_lower
                for keyword in ["audit", "control", "security", "compliance", "policy"]
            ):
                relevance_score += 25
        if evidence.evidence_type and evidence.evidence_type != "unknown":
            relevance_score += 25
        scores["relevance"] = min(relevance_score, 100)

        return scores

    def _combine_traditional_and_ai_scores(
        self, traditional_scores: Dict[str, float], ai_analysis: Dict[str, Any]
    ) -> float:
        """Combine traditional algorithmic scores with AI analysis scores."""
        try:
            # Get AI scores
            ai_scores = ai_analysis.get("scores", {})
            ai_confidence = ai_analysis.get("ai_confidence", 0)

            # Weight between traditional and AI based on AI confidence
            ai_weight = ai_confidence / 100  # 0-1 scale
            traditional_weight = 1 - ai_weight

            # Calculate traditional average
            traditional_avg = (
                sum(traditional_scores.values()) / len(traditional_scores)
                if traditional_scores
                else 50
            )

            # Calculate AI average
            ai_avg = ai_analysis.get("overall_score", 50) if ai_scores else 50

            # Combine scores
            final_score = (traditional_avg * traditional_weight) + (ai_avg * ai_weight)

            return round(final_score, 2)

        except Exception as e:
            logger.warning(f"Score combination failed: {e}")
            # Fall back to traditional score
            return (
                sum(traditional_scores.values()) / len(traditional_scores)
                if traditional_scores
                else 50.0
            )

    async def detect_semantic_duplicates(
        self,
        evidence: EvidenceItem,
        candidate_evidence: List[EvidenceItem],
        similarity_threshold: float = 0.8,
    ) -> List[Dict[str, Any]]:
        """
        Detect semantic duplicates using AI-powered content analysis.
        Goes beyond simple hash comparison to find conceptually similar evidence.
        """
        try:
            if not candidate_evidence:
                return []

            model = self._get_ai_model()
            duplicates = []

            # Prepare target evidence content
            target_content = self._prepare_content_for_analysis(evidence)

            # Check each candidate for semantic similarity
            for candidate in candidate_evidence:
                if candidate.id == evidence.id:
                    continue

                candidate_content = self._prepare_content_for_analysis(candidate)

                # AI-powered similarity analysis
                similarity_result = await self._analyze_semantic_similarity(
                    model, target_content, candidate_content, evidence, candidate
                )

                if similarity_result["similarity_score"] >= similarity_threshold * 100:
                    duplicates.append(
                        {
                            "candidate_id": candidate.id,
                            "candidate_name": candidate.evidence_name,
                            "similarity_score": similarity_result["similarity_score"],
                            "similarity_type": similarity_result["similarity_type"],
                            "reasoning": similarity_result["reasoning"],
                            "recommendation": similarity_result["recommendation"],
                        }
                    )

            # Sort by similarity score (highest first)
            duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)

            return duplicates

        except Exception as e:
            logger.error(
                f"Semantic duplicate detection failed for evidence {evidence.id}: {e}",
                exc_info=True,
            )
            return []

    async def _analyze_semantic_similarity(
        self,
        model,
        content1: str,
        content2: str,
        evidence1: EvidenceItem,
        evidence2: EvidenceItem,
    ) -> Dict[str, Any]:
        """Analyze semantic similarity between two pieces of evidence using AI."""
        try:
            similarity_prompt = f"""Compare these two compliance evidence items for semantic similarity:

EVIDENCE 1:
{content1}

EVIDENCE 2:
{content2}

Analyze:
1. CONTENT_SIMILARITY: How similar is the actual content/information? (0-100)
2. PURPOSE_SIMILARITY: Do they serve the same compliance purpose? (0-100)
3. SCOPE_OVERLAP: How much do their scopes overlap? (0-100)

Determine:
- SIMILARITY_TYPE: exact_duplicate, substantial_overlap, partial_overlap, or different
- OVERALL_SIMILARITY: Average of the three scores above
- REASONING: Brief explanation of similarities/differences
- RECOMMENDATION: merge, keep_both, or review_manually

Format response as:
CONTENT_SIMILARITY: [score]
PURPOSE_SIMILARITY: [score]
SCOPE_OVERLAP: [score]
OVERALL_SIMILARITY: [score]
SIMILARITY_TYPE: [type]
REASONING: [explanation]
RECOMMENDATION: [action]"""

            # Use asyncio to run the AI model in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, model.generate_content, similarity_prompt
            )

            return self._parse_similarity_response(response.text)

        except Exception as e:
            logger.warning(f"AI similarity analysis failed: {e}")
            return {
                "similarity_score": 0,
                "similarity_type": "different",
                "reasoning": "Analysis failed",
                "recommendation": "review_manually",
            }

    def _parse_similarity_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI similarity analysis response."""
        try:
            result = {
                "similarity_score": 0,
                "similarity_type": "different",
                "reasoning": "No analysis available",
                "recommendation": "review_manually",
            }

            lines = response_text.strip().split("\n")
            scores = []

            for line in lines:
                line = line.strip()

                if ":" in line:
                    parts = line.split(":", 1)
                    key = parts[0].strip().upper()
                    value = parts[1].strip()

                    # Parse similarity scores
                    if key in [
                        "CONTENT_SIMILARITY",
                        "PURPOSE_SIMILARITY",
                        "SCOPE_OVERLAP",
                        "OVERALL_SIMILARITY",
                    ]:
                        try:
                            score = int(re.search(r"\d+", value).group())
                            score = max(0, min(100, score))  # Clamp to 0-100
                            scores.append(score)
                            if key == "OVERALL_SIMILARITY":
                                result["similarity_score"] = score
                        except (ValueError, AttributeError):
                            continue

                    # Parse similarity type
                    elif key == "SIMILARITY_TYPE":
                        if value.lower() in [
                            "exact_duplicate",
                            "substantial_overlap",
                            "partial_overlap",
                            "different",
                        ]:
                            result["similarity_type"] = value.lower()

                    # Parse reasoning
                    elif key == "REASONING":
                        result["reasoning"] = value

                    # Parse recommendation
                    elif key == "RECOMMENDATION":
                        if value.lower() in ["merge", "keep_both", "review_manually"]:
                            result["recommendation"] = value.lower()

            # Calculate overall similarity if not provided
            if result["similarity_score"] == 0 and scores:
                result["similarity_score"] = sum(scores) / len(scores)

            return result

        except Exception as e:
            logger.warning(f"Failed to parse similarity response: {e}")
            return {
                "similarity_score": 0,
                "similarity_type": "different",
                "reasoning": "Parsing failed",
                "recommendation": "review_manually",
            }

    async def batch_duplicate_detection(
        self, evidence_items: List[EvidenceItem], similarity_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Perform batch duplicate detection across multiple evidence items.
        Returns a comprehensive duplicate analysis report.
        """
        try:
            if len(evidence_items) < 2:
                return {
                    "total_items": len(evidence_items),
                    "duplicate_groups": [],
                    "potential_duplicates": 0,
                    "analysis_summary": "Insufficient items for duplicate detection",
                }

            duplicate_groups = []
            processed_ids = set()

            for i, evidence in enumerate(evidence_items):
                if evidence.id in processed_ids:
                    continue

                # Find duplicates for this evidence
                candidates = evidence_items[
                    i + 1 :
                ]  # Only check items after current one
                duplicates = await self.detect_semantic_duplicates(
                    evidence, candidates, similarity_threshold
                )

                if duplicates:
                    # Create duplicate group
                    group = {
                        "primary_evidence": {
                            "id": evidence.id,
                            "name": evidence.evidence_name,
                            "type": evidence.evidence_type,
                        },
                        "duplicates": duplicates,
                        "group_size": len(duplicates) + 1,
                        "highest_similarity": max(
                            d["similarity_score"] for d in duplicates
                        ),
                    }
                    duplicate_groups.append(group)

                    # Mark all items in this group as processed
                    processed_ids.add(evidence.id)
                    for dup in duplicates:
                        processed_ids.add(dup["candidate_id"])

            total_duplicates = sum(
                group["group_size"] - 1 for group in duplicate_groups
            )

            return {
                "total_items": len(evidence_items),
                "duplicate_groups": duplicate_groups,
                "potential_duplicates": total_duplicates,
                "unique_items": len(evidence_items) - total_duplicates,
                "analysis_summary": f"Found {len(duplicate_groups)} duplicate groups with {total_duplicates} potential duplicates",
            }

        except Exception as e:
            logger.error(f"Batch duplicate detection failed: {e}", exc_info=True)
            return {
                "total_items": len(evidence_items),
                "duplicate_groups": [],
                "potential_duplicates": 0,
                "analysis_summary": f"Analysis failed: {e!s}",
            }
