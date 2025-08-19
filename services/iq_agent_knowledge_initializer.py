"""
IQ Agent Knowledge Graph Initializer

This module creates the IQ Agent's individual knowledge structure separate from
the compliance graph. The IQ Agent has access to the compliance graph for
regulatory analysis but maintains its own decision patterns, learning memories,
and strategic insights.

Based on "The Proactive Compliance Mandate: A Strategic Blueprint for FinTech Leadership (2025-2030)"
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from services.neo4j_service import Neo4jGraphRAGService

logger = logging.getLogger(__name__)


@dataclass
class DecisionPattern:
    """IQ Agent decision pattern for compliance scenarios"""

    name: str
    category: str  # risk_evaluation, task_prioritization, technology_selection
    context: str
    decision_criteria: List[str]
    outcome_priorities: List[str]
    risk_factors: List[str]
    success_metrics: List[str]


@dataclass
class LearningMemory:
    """Stored learning and experience for the IQ Agent"""

    title: str
    domain: str  # AML, GDPR, operational_resilience, etc.
    key_insights: List[str]
    lessons_learned: List[str]
    application_context: str
    related_regulations: List[str]
    business_impact: str


@dataclass
class RegulatoryInsight:
    """Strategic regulatory intelligence"""

    topic: str
    trend_category: str  # convergence, emerging_tech, enforcement_patterns
    time_horizon: str  # 2025-2026, 2027-2030
    jurisdictions: List[str]
    strategic_implications: List[str]
    recommended_actions: List[str]
    confidence_level: str


@dataclass
class BusinessContext:
    """Business and strategic context for compliance decisions"""

    scenario: str
    business_function: str
    stakeholders: List[str]
    compliance_objectives: List[str]
    business_objectives: List[str]
    success_criteria: List[str]
    risk_appetite: str


class IQAgentKnowledgeInitializer:
    """Initializes IQ Agent's individual knowledge graph"""

    def __init__(self, neo4j_service: Neo4jGraphRAGService) -> None:
        self.neo4j = neo4j_service

    async def initialize_iq_agent_knowledge(self) -> Dict[str, Any]:
        """Initialize IQ Agent's individual knowledge structure"""
        try:
            logger.info("Starting IQ Agent knowledge graph initialization")

            # Clear existing IQ Agent knowledge
            await self._clear_iq_knowledge()

            # Create IQ-specific schema
            await self._create_iq_schema()

            # Load knowledge components
            decision_patterns = await self._load_decision_patterns()
            learning_memories = await self._load_learning_memories()
            regulatory_insights = await self._load_regulatory_insights()
            business_contexts = await self._load_business_contexts()
            adaptive_nodes = await self._load_adaptive_learning_nodes()

            # Create knowledge relationships
            relationships = await self._create_knowledge_relationships()

            result = {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "iq_agent_knowledge": {
                    "decision_patterns": decision_patterns,
                    "learning_memories": learning_memories,
                    "regulatory_insights": regulatory_insights,
                    "business_contexts": business_contexts,
                    "adaptive_learning_nodes": adaptive_nodes,
                },
                "relationships_created": relationships,
                "message": "IQ Agent knowledge graph initialization completed successfully",
            }

            logger.info(f"IQ Agent knowledge initialization completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to initialize IQ Agent knowledge: {str(e)}")
            return {"status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def _clear_iq_knowledge(self) -> None:
        """Clear existing IQ Agent knowledge"""
        query = """
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label IN [
            'DecisionPattern', 'LearningMemory', 'RegulatoryInsight',
            'BusinessContext', 'AdaptiveLearning', 'IQKnowledge'
        ])
        DETACH DELETE n
        """
        await self.neo4j.execute_query(query, read_only=False)
        logger.info("Cleared existing IQ Agent knowledge")

    async def _create_iq_schema(self) -> None:
        """Create IQ Agent schema constraints and indexes"""
        constraints = [
            "CREATE CONSTRAINT decision_pattern_name IF NOT EXISTS FOR (dp:DecisionPattern) REQUIRE dp.name IS UNIQUE",
            "CREATE CONSTRAINT learning_memory_title IF NOT EXISTS FOR (lm:LearningMemory) REQUIRE lm.title IS UNIQUE",
            "CREATE CONSTRAINT regulatory_insight_topic IF NOT EXISTS FOR (ri:RegulatoryInsight) REQUIRE ri.topic IS UNIQUE",
            "CREATE CONSTRAINT business_context_scenario IF NOT EXISTS FOR (bc:BusinessContext) REQUIRE bc.scenario IS UNIQUE",
        ]

        indexes = [
            "CREATE INDEX decision_pattern_category IF NOT EXISTS FOR (dp:DecisionPattern) ON (dp.category)",
            "CREATE INDEX learning_memory_domain IF NOT EXISTS FOR (lm:LearningMemory) ON (lm.domain)",
            "CREATE INDEX regulatory_insight_trend IF NOT EXISTS FOR (ri:RegulatoryInsight) ON (ri.trend_category)",
            "CREATE INDEX business_context_function IF NOT EXISTS FOR (bc:BusinessContext) ON (bc.business_function)",
        ]

        for constraint in constraints:
            try:
                await self.neo4j.execute_query(constraint, read_only=False)
            except Exception as e:
                logger.warning(f"IQ schema constraint warning: {e}")

        for index in indexes:
            try:
                await self.neo4j.execute_query(index, read_only=False)
            except Exception as e:
                logger.warning(f"IQ schema index warning: {e}")

        logger.info("IQ Agent schema constraints and indexes created")

    async def _load_decision_patterns(self) -> int:
        """Load decision patterns from the compliance playbook"""
        patterns = [
            DecisionPattern(
                name="Compliance Risk Evaluation Framework",
                category="risk_evaluation",
                context="Evaluating new regulatory requirements or compliance gaps",
                decision_criteria=[
                    "Regulatory severity and enforcement patterns",
                    "Potential for customer harm",
                    "Impact on strategic business objectives",
                    "Implementation complexity and cost",
                    "Reputational risk exposure",
                ],
                outcome_priorities=[
                    "Prevent existential regulatory risk",
                    "Maintain customer trust",
                    "Enable strategic growth initiatives",
                    "Optimize resource allocation",
                ],
                risk_factors=[
                    "Late SAR filing penalties (BaFin €6.5M Solaris case)",
                    "Systematic compliance failures (NYDFS $30M Robinhood case)",
                    "Cross-border data transfer violations",
                    "AI bias and discrimination risks",
                ],
                success_metrics=[
                    "Zero regulatory fines or enforcement actions",
                    "Average SAR filing time <15 days",
                    "Customer data breach notification <72 hours",
                    "AML false positive rate <80%",
                ],
            ),
            DecisionPattern(
                name="Technology Investment Prioritization",
                category="technology_selection",
                context="Selecting and prioritizing compliance technology investments",
                decision_criteria=[
                    "Automation potential for manual processes",
                    "Integration capability with existing systems",
                    "Scalability across multiple jurisdictions",
                    "ROI through efficiency gains or risk reduction",
                    "Vendor security and resilience posture",
                ],
                outcome_priorities=[
                    "Maximize automation of compliance controls",
                    "Reduce operational risk through technology",
                    "Enable real-time compliance monitoring",
                    "Create audit-ready evidence trails",
                ],
                risk_factors=[
                    "Vendor concentration risk (DORA third-party oversight)",
                    "Technology implementation delays",
                    "Integration complexity and downtime",
                    "Data security and privacy implications",
                ],
                success_metrics=[
                    "40% reduction in manual audit preparation time",
                    "95%+ accuracy in transaction monitoring",
                    "100% automated sanctions screening",
                    "24-hour average DSAR fulfillment time",
                ],
            ),
            DecisionPattern(
                name="Proactive vs Reactive Compliance Strategy",
                category="task_prioritization",
                context="Balancing proactive compliance investments vs reactive gap remediation",
                decision_criteria=[
                    "Regulatory timeline and phase-in periods",
                    "Competitive advantage through early adoption",
                    "Resource constraints and opportunity cost",
                    "Market access and licensing requirements",
                    "Customer and investor expectations",
                ],
                outcome_priorities=[
                    "Build sustainable compliance moat",
                    "Enable faster market entry",
                    "Reduce compliance debt accumulation",
                    "Demonstrate regulatory leadership",
                ],
                risk_factors=[
                    "Regulatory debt compound interest",
                    "Surprise examination findings",
                    "Competitive disadvantage from late adoption",
                    "Resource drain from crisis management",
                ],
                success_metrics=[
                    "First-mover advantage in new markets",
                    "Regulator relationship quality score",
                    "Time-to-market for new products",
                    "Enterprise customer acquisition rate",
                ],
            ),
        ]

        query = """
        UNWIND $patterns AS pattern
        CREATE (dp:DecisionPattern {
            name: pattern.name,
            category: pattern.category,
            context: pattern.context,
            decision_criteria: pattern.decision_criteria,
            outcome_priorities: pattern.outcome_priorities,
            risk_factors: pattern.risk_factors,
            success_metrics: pattern.success_metrics,
            created_at: datetime()
        })
        """

        pattern_dicts = [asdict(pattern) for pattern in patterns]
        await self.neo4j.execute_query(query, {"patterns": pattern_dicts}, read_only=False)
        logger.info(f"Created {len(patterns)} decision patterns")
        return len(patterns)

    async def _load_learning_memories(self) -> int:
        """Load learning memories from compliance playbook insights"""
        memories = [
            LearningMemory(
                title="GDPR Privacy by Design Implementation",
                domain="data_protection",
                key_insights=[
                    "Privacy controls must be embedded in product development lifecycle",
                    "DPIA mandatory for high-risk processing including AI/ML",
                    "Data minimization principle requires purpose limitation",
                    "Cross-border transfer mechanisms critical post-Schrems II",
                ],
                lessons_learned=[
                    "Generic privacy policies insufficient for GDPR compliance",
                    "Manual DSAR handling cannot scale beyond 100s of requests",
                    "Consent fatigue reduces user experience and legal validity",
                    "Privacy controls require engineering partnership, not just legal review",
                ],
                application_context="New product features involving personal data collection or AI processing",
                related_regulations=["GDPR", "DPA2018", "CCPA", "CPRA"],
                business_impact="Enables EU market access, builds customer trust, prevents €20M+ fines",
            ),
            LearningMemory(
                title="AML Transaction Monitoring Optimization",
                domain="financial_crime",
                key_insights=[
                    "AI-powered monitoring reduces false positives from 95%+ to <80%",
                    "Risk-based approach more effective than threshold-based rules",
                    "Real-time screening prevents prohibited transactions",
                    "Analyst time reallocation improves SAR quality",
                ],
                lessons_learned=[
                    "Manual monitoring cannot scale with transaction volume",
                    "Late SAR filing triggers automatic regulatory scrutiny",
                    "Sanctions screening gaps create strict liability exposure",
                    "Training data bias can perpetuate discriminatory outcomes",
                ],
                application_context="Transaction processing systems and customer onboarding workflows",
                related_regulations=["6AMLD", "BSA", "MLR2017", "OFAC"],
                business_impact="Prevents multi-million dollar fines, enables payment partnerships, protects reputation",
            ),
            LearningMemory(
                title="Operational Resilience and DORA Compliance",
                domain="operational_risk",
                key_insights=[
                    "Critical business services mapping essential for resilience",
                    "Third-party vendor concentration creates systemic risk",
                    "Incident response must include regulatory notification",
                    "Recovery time objectives must be quantified and tested",
                ],
                lessons_learned=[
                    "Cloud provider outages can halt entire business operations",
                    "Vendor due diligence cannot be annual checkbox exercise",
                    "Incident communication speed affects regulatory perception",
                    "Business continuity plans require regular testing and updates",
                ],
                application_context="Technology infrastructure decisions and vendor management",
                related_regulations=["DORA", "PRA", "FCA_Operational_Resilience"],
                business_impact="Ensures service availability, prevents operational losses, maintains market confidence",
            ),
        ]

        query = """
        UNWIND $memories AS memory
        CREATE (lm:LearningMemory {
            title: memory.title,
            domain: memory.domain,
            key_insights: memory.key_insights,
            lessons_learned: memory.lessons_learned,
            application_context: memory.application_context,
            related_regulations: memory.related_regulations,
            business_impact: memory.business_impact,
            created_at: datetime()
        })
        """

        memory_dicts = [asdict(memory) for memory in memories]
        await self.neo4j.execute_query(query, {"memories": memory_dicts}, read_only=False)
        logger.info(f"Created {len(memories)} learning memories")
        return len(memories)

    async def _load_regulatory_insights(self) -> int:
        """Load regulatory trend insights from the playbook"""
        insights = [
            RegulatoryInsight(
                topic="Global Operational Resilience Convergence",
                trend_category="convergence",
                time_horizon="2025-2026",
                jurisdictions=["EU", "UK", "US"],
                strategic_implications=[
                    "Unified Enterprise Resilience Framework more efficient than jurisdiction-specific approaches",
                    "First-movers gain competitive advantage through superior resilience posture",
                    "Vendor concentration risk becomes primary regulatory focus",
                    "Quantified impact tolerances replace qualitative risk statements",
                ],
                recommended_actions=[
                    "Map critical business services across all jurisdictions",
                    "Implement unified vendor risk management framework",
                    "Establish quantified recovery time objectives",
                    "Conduct cross-functional resilience testing",
                ],
                confidence_level="high",
            ),
            RegulatoryInsight(
                topic="AI Governance Regulatory Frameworks",
                trend_category="emerging_tech",
                time_horizon="2025-2027",
                jurisdictions=["EU", "UK", "US"],
                strategic_implications=[
                    "EU AI Act sets global standard for high-risk AI systems",
                    "Algorithmic bias testing becomes mandatory for financial services AI",
                    "Model explainability requirements impact AI architecture decisions",
                    "MLOps pipelines must embed governance controls",
                ],
                recommended_actions=[
                    "Inventory all AI/ML models by risk category",
                    "Implement bias testing in MLOps pipeline",
                    "Establish AI model governance board",
                    "Prepare for algorithmic impact assessments",
                ],
                confidence_level="high",
            ),
            RegulatoryInsight(
                topic="Crypto Asset Regulatory Formalization",
                trend_category="emerging_tech",
                time_horizon="2025-2030",
                jurisdictions=["EU", "UK", "US"],
                strategic_implications=[
                    "MiCA-like frameworks becoming global template",
                    "Stablecoin reserve transparency requirements standardizing",
                    "Market surveillance obligations extending to crypto",
                    "Licensing requirements creating barriers to entry",
                ],
                recommended_actions=[
                    "Implement MiCA-compliant governance framework",
                    "Deploy crypto market surveillance tools",
                    "Prepare for asset listing due diligence requirements",
                    "Establish stablecoin reserve audit procedures",
                ],
                confidence_level="medium",
            ),
            RegulatoryInsight(
                topic="ESG and Climate Disclosure Expansion",
                trend_category="disclosure_requirements",
                time_horizon="2025-2030",
                jurisdictions=["EU", "UK", "US"],
                strategic_implications=[
                    "ESG performance affects access to capital and customers",
                    "Anti-greenwashing rules create liability for unsubstantiated claims",
                    "Supply chain ESG data collection becomes mandatory",
                    "Climate scenario analysis required for risk management",
                ],
                recommended_actions=[
                    "Begin voluntary TCFD-aligned reporting",
                    "Implement ESG data collection systems",
                    "Establish anti-greenwashing review processes",
                    "Conduct climate risk scenario analysis",
                ],
                confidence_level="high",
            ),
        ]

        query = """
        UNWIND $insights AS insight
        CREATE (ri:RegulatoryInsight {
            topic: insight.topic,
            trend_category: insight.trend_category,
            time_horizon: insight.time_horizon,
            jurisdictions: insight.jurisdictions,
            strategic_implications: insight.strategic_implications,
            recommended_actions: insight.recommended_actions,
            confidence_level: insight.confidence_level,
            created_at: datetime()
        })
        """

        insight_dicts = [asdict(insight) for insight in insights]
        await self.neo4j.execute_query(query, {"insights": insight_dicts}, read_only=False)
        logger.info(f"Created {len(insights)} regulatory insights")
        return len(insights)

    async def _load_business_contexts(self) -> int:
        """Load business context scenarios for compliance decision-making"""
        contexts = [
            BusinessContext(
                scenario="New Market Entry - EU Financial Services",
                business_function="market_expansion",
                stakeholders=["CEO", "CFO", "Head of Product", "Legal", "CCO"],
                compliance_objectives=[
                    "Obtain regulatory approval for EU operations",
                    "Demonstrate GDPR and DORA compliance",
                    "Establish local data processing capabilities",
                    "Implement MiCA-compliant crypto framework",
                ],
                business_objectives=[
                    "Capture 5% market share in target EU countries",
                    "Launch localized product offerings",
                    "Establish enterprise customer relationships",
                    "Generate €50M ARR within 24 months",
                ],
                success_criteria=[
                    "Regulatory approval within 12 months",
                    "Zero compliance violations in first year",
                    "Customer acquisition cost <€100",
                    "Net Promoter Score >70",
                ],
                risk_appetite="conservative",
            ),
            BusinessContext(
                scenario="AI-Powered Credit Scoring Implementation",
                business_function="product_development",
                stakeholders=["CTO", "Head of Data Science", "Head of Product", "CCO", "Legal"],
                compliance_objectives=[
                    "Ensure AI model fairness and non-discrimination",
                    "Implement explainable AI requirements",
                    "Establish model governance framework",
                    "Comply with emerging AI regulations",
                ],
                business_objectives=[
                    "Improve credit decision accuracy by 15%",
                    "Reduce manual underwriting by 60%",
                    "Expand addressable market to thin-file customers",
                    "Maintain sub-5% default rate",
                ],
                success_criteria=[
                    "Model bias testing shows no protected class discrimination",
                    "Regulatory approval for model deployment",
                    "Customer satisfaction with decisioning speed",
                    "Audit-ready model documentation",
                ],
                risk_appetite="moderate",
            ),
            BusinessContext(
                scenario="Third-Party Vendor Risk Management (DORA Compliance)",
                business_function="risk_management",
                stakeholders=["CRO", "CCO", "CTO", "Procurement", "Legal"],
                compliance_objectives=[
                    "Identify and assess critical ICT third-party providers",
                    "Implement DORA-compliant vendor oversight",
                    "Establish vendor incident notification procedures",
                    "Develop vendor exit strategies",
                ],
                business_objectives=[
                    "Maintain 99.9% system uptime",
                    "Reduce vendor-related incidents by 50%",
                    "Optimize vendor costs through consolidation",
                    "Improve negotiating position with vendors",
                ],
                success_criteria=[
                    "100% of critical vendors assessed annually",
                    "Vendor incident response <4 hours",
                    "Successful vendor exit simulation",
                    "Regulatory approval of vendor framework",
                ],
                risk_appetite="conservative",
            ),
        ]

        query = """
        UNWIND $contexts AS context
        CREATE (bc:BusinessContext {
            scenario: context.scenario,
            business_function: context.business_function,
            stakeholders: context.stakeholders,
            compliance_objectives: context.compliance_objectives,
            business_objectives: context.business_objectives,
            success_criteria: context.success_criteria,
            risk_appetite: context.risk_appetite,
            created_at: datetime()
        })
        """

        context_dicts = [asdict(context) for context in contexts]
        await self.neo4j.execute_query(query, {"contexts": context_dicts}, read_only=False)
        logger.info(f"Created {len(contexts)} business contexts")
        return len(contexts)

    async def _load_adaptive_learning_nodes(self) -> int:
        """Load adaptive learning capabilities for the IQ Agent"""
        query = """
        CREATE
        (al1:AdaptiveLearning {
            name: "Regulatory Pattern Recognition",
            learning_type: "pattern_optimization",
            description: "Continuously learns from regulatory enforcement patterns to predict emerging risks",
            capabilities: [
                "Enforcement action pattern analysis",
                "Regulatory communication sentiment analysis",
                "Cross-jurisdictional trend correlation",
                "Early warning signal detection"
            ],
            data_sources: [
                "Regulatory enforcement databases",
                "Industry compliance incident reports",
                "Regulatory consultation papers",
                "Compliance cost-benefit analyses"
            ],
            update_frequency: "weekly",
            confidence_threshold: 0.75,
            created_at: datetime()
        }),
        (al2:AdaptiveLearning {
            name: "Decision Context Adaptation",
            learning_type: "context_adaptation",
            description: "Adapts decision-making based on organization's compliance history and business context",
            capabilities: [
                "Risk appetite calibration",
                "Success metric optimization",
                "Resource allocation efficiency",
                "Stakeholder preference learning"
            ],
            data_sources: [
                "Historical compliance decisions",
                "Business outcome measurements",
                "Stakeholder feedback loops",
                "Resource utilization metrics"
            ],
            update_frequency: "monthly",
            confidence_threshold: 0.80,
            created_at: datetime()
        }),
        (al3:AdaptiveLearning {
            name: "Technology Effectiveness Assessment",
            learning_type: "performance_optimization",
            description: "Learns from compliance technology performance to recommend optimal tool configurations",
            capabilities: [
                "False positive rate optimization",
                "Process automation ROI analysis",
                "Tool integration efficiency",
                "Performance benchmark calibration"
            ],
            data_sources: [
                "Compliance tool performance metrics",
                "Process efficiency measurements",
                "Technology vendor assessments",
                "User experience feedback"
            ],
            update_frequency: "daily",
            confidence_threshold: 0.85,
            created_at: datetime()
        })
        """

        await self.neo4j.execute_query(query, read_only=False)
        logger.info("Created 3 adaptive learning nodes")
        return 3

    async def _create_knowledge_relationships(self) -> int:
        """Create relationships between IQ Agent knowledge components"""
        relationship_queries = [
            # Decision patterns to learning memories
            """
            MATCH (dp:DecisionPattern), (lm:LearningMemory)
            WHERE dp.category = "risk_evaluation" AND lm.domain IN ["data_protection", "financial_crime", "operational_risk"]
            CREATE (dp)-[:INFORMED_BY]->(lm)
            """,
            # Regulatory insights to decision patterns
            """
            MATCH (ri:RegulatoryInsight), (dp:DecisionPattern)
            WHERE ri.trend_category = "convergence" AND dp.category = "task_prioritization"
            CREATE (ri)-[:INFLUENCES]->(dp)
            """,
            # Business contexts to decision patterns
            """
            MATCH (bc:BusinessContext), (dp:DecisionPattern)
            WHERE bc.risk_appetite = "conservative" AND dp.category = "risk_evaluation"
            CREATE (bc)-[:REQUIRES]->(dp)
            """,
            # Adaptive learning to all knowledge types
            """
            MATCH (al:AdaptiveLearning {learning_type: "pattern_optimization"}), (ri:RegulatoryInsight)
            CREATE (al)-[:OPTIMIZES]->(ri)
            """,
            """
            MATCH (al:AdaptiveLearning {learning_type: "context_adaptation"}), (bc:BusinessContext)
            CREATE (al)-[:ADAPTS_TO]->(bc)
            """,
            """
            MATCH (al:AdaptiveLearning {learning_type: "performance_optimization"}), (dp:DecisionPattern)
            WHERE dp.category = "technology_selection"
            CREATE (al)-[:ENHANCES]->(dp)
            """,
            # Cross-domain knowledge relationships
            """
            MATCH (lm1:LearningMemory), (lm2:LearningMemory)
            WHERE lm1.domain <> lm2.domain
            AND any(reg IN lm1.related_regulations WHERE reg IN lm2.related_regulations)
            CREATE (lm1)-[:SHARES_REGULATORY_SCOPE]->(lm2)
            """,
            # Timeline-based insight relationships
            """
            MATCH (ri1:RegulatoryInsight), (ri2:RegulatoryInsight)
            WHERE ri1.time_horizon = "2025-2026" AND ri2.time_horizon = "2025-2027"
            AND any(jurisdiction IN ri1.jurisdictions WHERE jurisdiction IN ri2.jurisdictions)
            CREATE (ri1)-[:PRECEDES]->(ri2)
            """,
        ]

        total_relationships = 0
        for query in relationship_queries:
            await self.neo4j.execute_query(query, read_only=False)
            total_relationships += 1

        logger.info(f"Created {len(relationship_queries)} IQ knowledge relationship patterns")
        return len(relationship_queries)


async def initialize_iq_agent_knowledge() -> Dict[str, Any]:
    """Standalone function to initialize IQ Agent knowledge graph"""
    neo4j_service = Neo4jGraphRAGService()
    initializer = IQAgentKnowledgeInitializer(neo4j_service)

    try:
        await neo4j_service.initialize()
        result = await initializer.initialize_iq_agent_knowledge()
        return result
    finally:
        await neo4j_service.close()


if __name__ == "__main__":
    # For standalone execution
    async def main() -> None:
        result = await initialize_iq_agent_knowledge()
        print(f"IQ Agent knowledge initialization result: {result}")

    asyncio.run(main())
